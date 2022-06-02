import os
from typing import List, Dict, Collection, Tuple, Union
import pydantic
import pandas
import numpy
import pydantic
from walnut.models import CategoryBase, Category, CategoryMeta, Metalist
from walnut import common
from walnut import constants
from walnut.readers import Reader
from walnut.converters import IOCategory, IOMetalist
from walnut.FileIO import FileIO

def filter_cluster(content):
    if content.type == constants.METADATA_TYPE_NUMERIC:
        return content
    cluster_index = [0]*len(content.clusterName)
    new_cluster_name = []
    for idx, length in enumerate(content.clusterLength):
        if idx == 0 or length > 0:
            cluster_index[idx] = len(new_cluster_name)
            new_cluster_name.append(content.clusterName[idx])
    if len(new_cluster_name) != len(content.clusterName):
        for idx, id in enumerate(content.clusters):
            content.clusters[idx] = int(cluster_index[id])
            content.clusterName = new_cluster_name
            content.clusterLength = [length for idx, length in enumerate(content.clusterLength) if (idx == 0 or length > 0)]
    return content

def count_cluster_length(content):
    if content.type == constants.METADATA_TYPE_NUMERIC:
        return content
    if len(content.clusterName) < 1 or len(content.clusterLength) < 1:
        return content
    content.clusterLength = [0]*len(content.clusterName)
    for id in content.clusters:
        content.clusterLength[id] += 1
    return content

class Metadata:
    def __init__(self, metadata_folder: str, file_reader: Reader):
        self.__dir = metadata_folder
        self.__file_reader = file_reader
        self.__metalist = Metalist(content={})
        self.__categories: Dict[str, Category] = {}
        try:
            self.read()
        except:
            print("WARNING: Unable to initialize metadata")

    def read(self) -> None:
        self.__metalist = self.__get_metalist_io().read()
        self.__categories = self.__read_categories()

        self.__purge_invalid_categories()

    def write_metalist(self) -> None:
        self.__get_metalist_io().write(self.__metalist)
    
    def write_content_by_id(self, id) -> None:
        self.__get_category_io(id).write(self.__categories[id])

    def write_all(self) -> None:
        self.write_metalist
        for category_id in self.__categories:
            self.write_content_by_id(category_id)

    def to_df(self) -> pandas.DataFrame:
        df = pandas.DataFrame()
        names = [self.__metalist.get_category_meta(cate_key).name
                    for cate_key in self.__metalist.get_category_ids()]
        names, counts = numpy.unique(names, return_counts=True)
        name_index = {}
        for x, y in zip(names, counts):
            if y > 1:
                name_index[x] = 1

        for category_id, category in self.__categories.items():
            values = self.__metalist.get_category_data(category_id, category)
            name = self.__metalist.get_category_meta(category_id).name

            if name in name_index:
                name_with_index = "%s (%d)" % (name, name_index[name])
                name_index[name] += 1
            else:
                name_with_index = name

            df[name_with_index] = values

        return df

    def add_dataframe(self, category_data: pandas.DataFrame):
        for column_name in category_data:
            self.add_category(column_name, list(category_data[column_name]))

    def add_category(self, name: str, category_data: Collection):
        if len(self.__categories) > 0 \
                and len(category_data) != len(list(self.__categories.values())[0].clusters):
            raise ValueError("New category's length must equal existing lengths")
        try:
            numpy.array(category_data, dtype=float)
            is_numerical = True
        except ValueError:
            print("WARNING: Cannot add %s as a numerical type, treating as categorical" % name)
            is_numerical = False

        if is_numerical:
            category_base = CategoryBase(id=common.create_uuid(), name=name,
                                            history=[common.create_history()],
                                            type=constants.METADATA_TYPE_NUMERIC)
            new_category = Category(**category_base.dict(),
                                    clusters=list(numpy.array(category_data, dtype=float)))
        else:
            cluster_names, cluster_lengths = self.__get_cluster_names_and_lengths(category_data)
            category_base = CategoryBase(id=common.create_uuid(), name=name,
                                            clusterName=cluster_names,
                                            clusterLength=cluster_lengths,
                                            history=[common.create_history()],
                                            type=constants.METADATA_TYPE_CATEGORICAL)
            new_category = Category(**category_base.dict(),
                                    clusters=common.find_indices_in_list(category_data,
                                                                        cluster_names))
            if -1 in new_category.clusters:
                raise Exception("There is a huge bug in code")

        category_meta = CategoryMeta(**category_base.dict())
        self.__metalist.add_category(category_meta)
        self.__categories[category_meta.id] = new_category

    def change_reader(self, reader: Reader) -> None:
        self.__file_reader = reader

    def __get_cluster_names_and_lengths(self, category_data: Collection) -> Tuple[List[str], List[int]]:
        cluster_names, cluster_lengths = numpy.unique(category_data,
                                                        return_counts=True)
        if constants.UNASSIGNED in cluster_names:
            permutation = list(range(0, len(cluster_names)))
            index = numpy.where(cluster_names == constants.UNASSIGNED)[0][0]
            permutation[0], permutation[index] = permutation[index], permutation[0]
            cluster_names = cluster_names[permutation]
            cluster_lengths = cluster_lengths[permutation]
        else:
            cluster_names = numpy.array([constants.UNASSIGNED] + list(cluster_names))
            cluster_lengths = numpy.array([0] + list(cluster_lengths))

        return list(cluster_names), list(cluster_lengths)

    def __get_metalist_io(self) -> FileIO[Metalist]:
        return FileIO[Metalist](self.__get_metalist_path(),
                                    reader=self.__file_reader,
                                    converter=IOMetalist)

    def __get_category_io(self, category_id: str) -> FileIO[Category]:
        return FileIO[Category](self.__get_category_path(category_id),
                                    reader=self.__file_reader,
                                    converter=IOCategory)

    def __get_metalist_path(self) -> str:
        return os.path.join(self.__dir, "metalist.json")

    def __get_category_path(self, category_id: str) -> str:
        return os.path.join(self.__dir, f"{category_id}.json")

    def __read_categories(self) -> Dict[str, Category]:
        categories: Dict[str, Category] = {}
        for category_id in self.__metalist.get_category_ids():
            category_io = self.__get_category_io(category_id)
            try:
                items = {
                    "clusters": category_io.read().clusters,
                    **self.__metalist.get_category_meta(category_id).dict()
                }
                category = Category.parse_obj(items)
                categories[category_id] = category
            except pydantic.ValidationError as e:
                print("WARNING: Unable to parse category %s due to error: %s"
                        % (category_id, str(e)))
            except Exception as e:
                print("WARNING: Unable to read category %s due to error: %s"
                        % (category_id, str(e)))
        return categories

    def __purge_invalid_categories(self) -> None:
        existing_categories_id = [id for id in self.__categories]
        for invalid_category_id in numpy.setdiff1d(self.__metalist.get_category_ids(),
                                                    existing_categories_id):
            print("WARNING: Removing category %s due to not appearing in metalist"
                    % invalid_category_id)
            self.__metalist.remove_category(invalid_category_id)
    
    def get_content_by_id(self, id: str) -> Category:
        return self.__categories[id]

    def update_metadata(self, id:str, content:Category) -> None:
        # Update Category
        self.__categories[id] = content
        content_meta = content.__dict__.copy()
        content_meta.pop("clusters")
        
        # Update CategoryBase
        self.__metalist.content[id] = CategoryMeta.parse_obj(content_meta)

        # Write to file
        self.write_metalist()
        self.write_content_by_id(id)

    def add_label(self, category_id: str, value: Union[str, int, float], indices: List[int]) -> None:
        content = self.__categories[category_id]
        if content.type == constants.METADATA_TYPE_CATEGORICAL:
            assert isinstance(value, str)
            if value in content.clusterName:
                anno_id = content.clusterName.index(value)
            else:
                anno_id = len(content.clusterName)
                content.clusterName.append(value)

            for idx in indices:
                content.clusters[idx] = anno_id

        if content.type == constants.METADATA_TYPE_NUMERIC:
            assert isinstance(float(value), float)
            for idx in indices:
                content.clusters[idx] = float(value) # type: ignore
                # FIXME: creates a model for each metadata type

        # Update categories at category id
        filter_content = filter_cluster(count_cluster_length(content))
        filter_content.history.append(common.create_history(description="Edit metadata"))
        self.update_metadata(category_id, filter_content)