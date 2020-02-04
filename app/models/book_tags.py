from app.config import db


class BookTags(db.Model):  # the table book_tags in the form of a class, that was able by SQL Alchemy ORM
    __tablename__ = "book_tags"  #identifying the name of the table

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True) #the id column
    goodreads_book_id = db.Column(db.Integer) #the column containing the id of the books from the goodreads dataset
    tag_id = db.Column(db.Integer) #The column containing the id of the tags from the dataset
    tag_name = db.Column(db.String(120)) #the column containing the name of the tag corresponding to the tag id
    count = db.Column(db.Integer) 

    @classmethod
    def get_tags(cls, gid, n=5): 
        """Gets list of tags for a given book.

        Args:
            gid ([string]): Goodreads book id provided in the dataset.
                            Encountered as `goodreads_book_id`

        Returns:
            [List]: List of tag objects, each of which has a two fields (tag_id, count)
        """
        return [
            x.__dict__
            for x in (
                cls.query.filter_by(goodreads_book_id=gid)
                .order_by(cls.count.desc())
                .limit(n)
            )
        ]
