"""
Here is a simple module to schedule next revision step according to previous answer and current one.
You should only use revision_steps list from this module.
"""
from datetime import timedelta


class RevisionStep(object):
    """
    Represent a cell of revision table.
    """
    column = None
    """
    Index in revision table
    """
    next_time = (None, None, None)
    """
    Next wake up according to difficulty (easy, medium, hard)
    """
    next_column = (None, None, None)
    """
    Next column according to difficulty (easy, medium, hard)
    """

    def __init__(self, index, next_time):
        self.column = index
        self.next_time = next_time

    def create_link(self, next_column):
        self.next_column = next_column

    def get_next_column(self, difficulty):
        return self.next_column[difficulty]

    def get_next_time(self, difficulty):
        return self.next_time[difficulty]

#        Format is (index, (easy, medium, hard))

next_time_table = ((0, (timedelta(days=4), timedelta(days=2), timedelta(minutes=10))),
                   (1, (timedelta(days=4), timedelta(days=2), timedelta(minutes=10))),
                   (2, (timedelta(days=15), timedelta(days=4), timedelta(minutes=10))),
                   (3, (timedelta(days=30), timedelta(days=15), timedelta(days=1))),
                   (4, (timedelta(days=60), timedelta(days=30), timedelta(days=1))),
                   (5, (timedelta(days=90), timedelta(days=45), timedelta(days=1))),
                   (6, (timedelta(days=90), timedelta(days=45), timedelta(days=1))),
                   (7, (timedelta(days=120), timedelta(days=60), timedelta(days=1))),
                   (8, (timedelta(days=120), timedelta(days=75), timedelta(days=1))),
                   (9, (timedelta(days=180), timedelta(days=90), timedelta(days=1))))

next_column_table = ((0, (+2, +1, 0)),
                     (1, (+2, +1, 0)),
                     (2, (+2, +1, 0)),
                     (3, (+2, +1, 0)),
                     (4, (+2, +1, -1)),
                     (5, (+2, +1, -1)),
                     (6, (+2, +1, -1)),
                     (7, (+2, +1, -2)),
                     (8, (+1, +1, -2)),
                     (9, (0, 0, -2)))

revision_steps = [RevisionStep(i[0], i[1]) for i in next_time_table]
"""
This is actually the revision table.
"""

for i, rev in enumerate(revision_steps):
    rev.create_link((revision_steps[revision_steps[i].column+next_column_table[i][1][0]],
                     revision_steps[revision_steps[i].column+next_column_table[i][1][1]],
                     revision_steps[revision_steps[i].column+next_column_table[i][1][2]]))
