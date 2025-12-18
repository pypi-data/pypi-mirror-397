from dataclasses import dataclass

import pyarrow as pa


@dataclass
class Schema:
    """Schema wrapper class for DataFrame column information.

    Provides convenient access to column names, data types, and schema metadata.
    """

    _schema_dict: dict[str, pa.DataType]

    def dtypes(self) -> list[pa.DataType]:
        """Get the data types of all columns.

        Returns
        -------
        List of PyArrow data types for each column in schema order.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": ["a", "b", "c"]})
        >>> types = df.schema.dtypes()
        """
        return list(self._schema_dict.values())

    def len(self) -> int:
        """Get the number of columns in the schema.

        Returns
        -------
        Integer count of columns.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": ["a", "b", "c"]})
        >>> num_cols = df.schema.len()
        """
        return len(self._schema_dict)

    def names(self) -> list[str]:
        """Get the names of all columns.

        Returns
        -------
        List of column names in schema order.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": ["a", "b", "c"]})
        >>> col_names = df.schema.names()
        """
        return list(self._schema_dict)

    def __getitem__(self, item: str) -> pa.DataType:
        """Get the data type of a specific column.

        Parameters
        ----------
        item
            Column name.

        Returns
        -------
        PyArrow data type of the specified column.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> df = DataFrame.from_dict({"x": [1, 2, 3]})
        >>> dtype = df.schema["x"]
        """
        return self._schema_dict[item]

    def __len__(self) -> int:
        """Get the number of columns in the schema.

        Returns
        -------
        Integer count of columns.
        """
        return self.len()
