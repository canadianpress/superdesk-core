from . import BaseFormatter, utils


class TableCSVFormatter(BaseFormatter):

    MIMETYPE = "text/csv"
    SEPARATOR = "\t"

    def export(self, show, rundown, items):
        filename = f"Technical-{rundown['title']}.csv"
        subitems = utils.get_subitems()
        columns = utils.item_table_columns(subitems)
        data = "\n".join(
            [self.SEPARATOR.join(columns)]
            + [
                self.SEPARATOR.join(utils.item_table_data(show, rundown, item, i, subitems))
                for i, item in enumerate(items, start=1)
            ]
        )
        return data.encode("utf-8"), self.MIMETYPE, filename
