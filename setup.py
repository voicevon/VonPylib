from setuptools import setup



setup(
    name = 'VonPylib',
    version = '0.0.3',
    description = 'My own python liberary',
    py_modules = ["terminal_font",
                    "reprap_arm",
                    "mqtt_helper",
                    "singleton"
                    ],
    package_dir = {'': 'src'},
    # Optional
    author = 'Xuming Feng',
    author_email = 'voicevon@gmail.com',
    url = 'https://github.com/voicevon/VonPylib',


)
