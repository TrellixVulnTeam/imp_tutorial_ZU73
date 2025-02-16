#!/usr/bin/env python

import unittest
import os
import sys
import glob
import shutil
import subprocess
import tarfile


TOPDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                      '..', 'rnapolii'))
RESULTS = "https://salilab.org/ftp/tutorials/imp/rnapolii/results.tar.gz"
ANALYSIS = "https://salilab.org/ftp/tutorials/imp/rnapolii/analysis.tar.gz"


class Tests(unittest.TestCase):

    def clean_output(self):
        for subdir in ('pdbs', 'rmfs'):
            fp = os.path.join(TOPDIR, 'modeling', 'output', subdir)
            if os.path.exists(fp):
                shutil.rmtree(fp, ignore_errors=False)
        for name in ('best.scores.rex.py', 'initial.0.rmf3',
                     'stat.0.out', 'stat_replica.0.out'):
            fp = os.path.join(TOPDIR, 'modeling', 'output', name)
            if os.path.exists(fp):
                os.unlink(fp)
        for subdir in glob.glob(os.path.join(TOPDIR, 'analysis',
                                             'kmeans_*_*')):
            shutil.rmtree(subdir, ignore_errors=False)

    @unittest.skipIf(sys.version_info[0] == 2,
                     "Needs urllib.request from Python 3")
    def test_analysis_on_precomputed(self):
        """Make sure that analysis works on precomputed results"""
        import urllib.request
        self.clean_output()
        os.chdir(os.path.join(TOPDIR, 'analysis'))
        # Get and extract precomputed results
        with urllib.request.urlopen(RESULTS) as fh:
            with tarfile.open(fileobj=fh, mode='r:gz') as tf:
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tf)
        for subdir in os.listdir('results/output'):
            shutil.move('results/output/%s' % subdir, '../modeling/output/')

        # Run clustering
        subprocess.check_call(["python", 'clustering.py'])
        self.assertTrue(os.path.exists('kmeans_5_1/dist_matrix.pdf'))
        self.assertTrue(os.path.exists('kmeans_5_1/cluster.0/0.rmf3'))

        # Test analysis
        subprocess.check_call(["python", 'precision_rmsf.py'])
        self.assertTrue(os.path.exists('kmeans_5_1/precision.0.0.out'))

        subprocess.check_call(["python", 'accuracy.py'])

    @unittest.skipIf(sys.version_info[0] == 2,
                     "Needs urllib.request from Python 3")
    def test_accuracy_of_precomputed_analysis(self):
        """Make sure that precomputed analysis can be checked for accuracy"""
        import urllib.request
        self.clean_output()
        os.chdir(os.path.join(TOPDIR, 'analysis'))
        # Get and extract precomputed analysis
        with urllib.request.urlopen(ANALYSIS) as fh:
            with tarfile.open(fileobj=fh, mode='r:gz') as tf:
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tf)

        subprocess.check_call(["python", 'accuracy.py'])

    def test_complete(self):
        """Test modeling and analysis"""
        self.clean_output()
        # Run modeling
        os.chdir(os.path.join(TOPDIR, 'modeling'))
        subprocess.check_call(["python", 'modeling.py', "--test"])
        self.assertTrue(os.path.exists('output/rmfs/0.rmf3'))

        # Run clustering
        os.chdir(os.path.join(TOPDIR, 'analysis'))
        subprocess.check_call(["python", 'clustering.py', "--test"])
        self.assertTrue(os.path.exists('kmeans_5_1/dist_matrix.pdf'))
        self.assertTrue(os.path.exists('kmeans_5_1/cluster.0/0.rmf3'))

        # Test analysis
        subprocess.check_call(["python", 'precision_rmsf.py'])
        self.assertTrue(os.path.exists('kmeans_5_1/precision.0.0.out'))

        subprocess.check_call(["python", 'accuracy.py'])


if __name__ == '__main__':
    unittest.main()
