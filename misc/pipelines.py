POST_PIC_PIPELINE = [
    {
        '$sort': {'date': -1}
    },
    {
        '$lookup': {
            'from': 'users',
            'localField': 'username',
            'foreignField': 'username',
            'as': 'user'
        }
    },
    {
        '$unwind': '$user'
    },
    {
        '$addFields': {
            'pic_path': '$user.pic_path'
        }
    },
    {
        '$project': {
            'user': 0
        }
    }
]