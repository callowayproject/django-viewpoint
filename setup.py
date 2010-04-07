from distutils.core import setup
from viewpoint import __version__

setup(name='viewpoint',
      version=__version__,
      description='Blog app focused on UX and usability',
      long_description=open('README').read(),
      author='TWT WebDevs',
      author_email='webdev@washingtontimes.com',
      url='http://opensource.washingtontimes.com/projects/viewpoint',
      packages=['viewpoint'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      )
