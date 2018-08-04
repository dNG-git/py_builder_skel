# -*- coding: utf-8 -*-

"""
builderSuite
Build code for different release targets
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?py;builder_suite

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(builderSuiteVersion)#
#echo(__FILEPATH__)#
"""

from os import path

from dNG.distutils.copy_builder import CopyBuilder

class InstallCopiedAndExtendedData(object):
    """
This class provides the callback to copy and extend source files with the
requested extensions.

:author:    direct Netware Group
:copyright: direct Netware Group - All rights reserved
:package:   builderSuite
:since:     v1.0.0
:license:   https://www.direct-netware.de/redirect?licenses;mpl2
            Mozilla Public License, v. 2.0
    """

    @staticmethod
    def callback(source_dir_path, target_path, target_parameters):
        """
Callback to be used in "dNG.distutils.InstallData".

:param source_dir_path: Source directory to copy files in
:param target_path: Target directory for build
:param target_parameters: Target parameters

:since: v1.0.0
        """

        target_extensions = target_parameters.get("copy_builder_extensions")

        if (type(target_extensions) is list and len(target_extensions) > 0):
            copy_builder = CopyBuilder(target_parameters,
                                       source_dir_path,
                                       target_path,
                                       target_extensions,
                                       default_chmod_files = "0644",
                                       default_chmod_dirs = "0755"
                                      )

            if (target_parameters.get("copy_builder_strip_source_dir_path", False)):
                copy_builder.set_strip_prefix(source_dir_path + path.sep)
            #

            copy_builder.make_all()
        #
    #
#