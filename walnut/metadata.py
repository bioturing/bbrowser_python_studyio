import os
import pydantic
from typing import List, Dict, Collection, Tuple
import pandas
import numpy

from walnut.models import CategoryBase, Category, CategoryMeta, Metalist
from walnut import common
from walnut import constants
from walnut.readers import Reader
from walnut.converters import IOCategory, IOMetalist
from walnut.FileIO import FileIO

class Metadata:
    def __init__(self, metadata_folder: str, file_reader: Reader):
        self.__dir = metadata_folder
        self.__file_reader = file_reader
        self.__metalist: Metalist = None
        self.__categories: Dict[str, Category] = {}

        self.read()

    def read(self) -> None:
        self.__metalist = self.__get_metalist_io().read()

        self.__read_categories()

        self.__purge_invalid_categories()

    def write(self) -> None:
        self.__get_metalist_io().write(self.__metalist)
        for category_id in self.__categories:
            io = self.__get_category_io(category_id)
            category = self.__categories[category_id]
            io.write(category)

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
                #assert("There is a huge bug in code")

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
        return os.path.join(self.__dir, category_id + ".json")

    def __read_categories(self) -> None:
        for category_id in self.__metalist.get_category_ids():
            category_io = self.__get_category_io(category_id)
            try:
                items = {
                    "clusters": category_io.read().clusters,
                    **self.__metalist.get_category_meta(category_id).dict()
                }
                category = Category.parse_obj(items)
            except pydantic.ValidationError as e:
                print("WARNING: Unable to parse category %s due to error: %s"
                        % (category_id, str(e)))
            except Exception as e:
                print("WARNING: Unable to read category %s due to error: %s"
                        % (category_id, str(e)))

            self.__categories[category_id] = category

    def __purge_invalid_categories(self) -> None:
        existing_categories_id = [id for id in self.__categories]
        for invalid_category_id in numpy.setdiff1d(self.__metalist.get_category_ids(),
                                                    existing_categories_id):
            print("WARNING: Removing category %s due to not appearing in metalist"
                    % invalid_category_id)
            self.__metalist.remove_category(invalid_category_id)
