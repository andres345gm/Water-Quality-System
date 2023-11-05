from MeasureRepository import MeasureRepository


# Class MeasureService
class MeasureService:

    # Method: Constructor
    def __init__(self):
        self.repository = MeasureRepository()

    # end def

    # Method: Insert measure into database
    def insert_measure(self, measure):
        self.repository.insert_measure(measure)

    # end def

# end class
