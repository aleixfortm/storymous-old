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

def pic_to_following_pipeline(usernames_list):
    pipeline = [
        {   '$match': {            
                'username': {'$in': usernames_list}
            }
        },
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

    return pipeline