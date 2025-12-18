import pkgutil

LANG={
    'en': {
        'det': 'det.onnx',
        'rec': 'rec.onnx',
        'cls': 'cls.onnx',
        'dict': 'ppocrv5_dict.txt',
    },
    'zhs': {
        'det': 'det.onnx',
        'rec': 'rec.onnx',
        'cls': 'cls.onnx',
        'dict': 'ppocrv5_dict.txt',
    },
    'zht': {
        'det': 'det.onnx',
        'rec': 'rec.onnx',
        'cls': 'cls.onnx',
        'dict': 'ppocrv5_dict.txt',
    },
    'ja': {
        'det': 'det.onnx',
        'rec': 'rec.onnx',
        'cls': 'cls.onnx',
        'dict': 'ppocrv5_dict.txt',
    },
}


def get_model_data(lang, step):
    return pkgutil.get_data(__name__, 'model/' + LANG[lang.lower()][step])


def get_character_dict(lang):
    return pkgutil.get_data(__name__, 'model/' + LANG[lang.lower()]['dict']).decode('utf-8').splitlines()


class OperatorGroup:
    def __init__(self, *ops):
        self.ops = ops

    def __call__(self, data):
        for op in self.ops:
            data = op(data)
        return data
