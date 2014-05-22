# -*- coding: utf-8 -*-
##j## BOF

"""
builderSkel
Common skeleton for builder tools
"""
"""n// NOTE
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
http://www.direct-netware.de/redirect.py?builderSkel

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
http://www.direct-netware.de/redirect.py?licenses;mpl2
----------------------------------------------------------------------------
#echo(builderSkelVersion)#
#echo(__FILEPATH__)#
----------------------------------------------------------------------------
NOTE_END //n"""

# pylint: disable=import-error,invalid-name,undefined-variable

from os import path
from time import time
import os
import re
import sys

try: import hashlib
except ImportError: import md5 as hashlib

try: import cPickle as pickle
except ImportError: import pickle

from file import File

try:
#
	_PY_BYTES = unicode.encode
	_PY_BYTES_TYPE = str
	_PY_STR = unicode.encode
	_PY_UNICODE_TYPE = unicode
#
except NameError:
#
	_PY_BYTES = str.encode
	_PY_BYTES_TYPE = bytes
	_PY_STR = bytes.decode
	_PY_UNICODE_TYPE = str
#

class BuilderSkel(object):
#
	"""
Provides a Python "make" environment skeleton.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    ext_core
:subpackage: builderSkel
:since:      v0.1.00
:license:    http://www.direct-netware.de/redirect.py?licenses;mpl2
             Mozilla Public License, v. 2.0
	"""

	# pylint: disable=unused-argument

	def __init__(self, parameters, include, output_path, filetype, default_umask = None, default_chmod_files = None, default_chmod_dirs = None, timeout_retries = 5, event_handler = None):
	#
		"""
Constructor __init__(BuilderSkel)

:param parameters: DEFINE statements
:param include: String (delimiter is ",") with directory or file names to
                be included.
:param output_path: Output path
:param filetype: String (delimiter is ",") with extensions of files to be
                 parsed.
:param default_umask umask: to set before creating new directories or files
:param default_chmod_files: chmod to set when creating a new file
:param default_chmod_dirs: chmod to set when creating a new directory
:param timeout_retries: Retries before timing out
:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		self.chmod_dirs = (0o750 if (default_chmod_dirs == None) else int(default_chmod_dirs, 8))
		"""
chmod to set when creating a new directory
		"""
		self.chmod_files = default_chmod_files
		"""
chmod to set when creating a new file
		"""
		self.dir_list = [ ]
		"""
Directories to be scanned
		"""
		self.dir_exclude_list = [ ]
		"""
Directories to be ignored while scanning
		"""
		self.event_handler = event_handler
		"""
The EventHandler is called whenever debug messages should be logged or errors
happened.
		"""
		self.file_dict = { }
		"""
Files to be parsed
		"""
		self.file_exclude_list = [ ]
		"""
Files to be ignored while scanning
		"""
		self.filetype_list = [ ]
		"""
Filetype extensions to be parsed
		"""
		self.filetype_ascii_list = [ "txt", "js", "php", "py", "xml" ]
		"""
Filetype extensions to be parsed
		"""
		self.output_path = ""
		"""
Path to generate the output files
		"""
		self.output_strip_prefix = ""
		"""
Prefix to be stripped from output paths
		"""
		self.parameters = { }
		"""
DEFINE values
		"""
		self.parser_list = None
		"""
Tags to be scanned for
		"""
		self.parser_pickle = { }
		"""
md5 strings of parsed files
		"""
		self.parser_tag = None
		"""
Tag identifier
		"""
		self.timeout_retries = timeout_retries
		"""
Retries before timing out
		"""
		self.umask = default_umask
		"""
umask to set before creating a new file
		"""
		self.workdir_rescan = True
		"""
umask to set before creating a new file
		"""

		self.set_new_target(parameters, include, output_path, filetype)
	#

	def add_filetype_ascii(self, extension):
	#
		"""
Adds an extension to the list of ASCII file types.

:param extension: File type extension to add
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE
		if (_PY_UNICODE_TYPE != str and type(extension) == _PY_UNICODE_TYPE): extension = _PY_STR(extension, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel.add_filetype_ascii({0})- (#echo(__LINE__)#)".format(extension))
		self.filetype_ascii_list.append(extension)
	#

	def _change_match(self, tag_definition, data, tag_position, data_position, tag_end_position):
	#
		"""
Change data according to the matched tag.

:param tag_definition: Matched tag definition
:param data: Data to be parsed
:param tag_position: Tag starting position
:param data_position: Data starting position
:param tag_end_position: Starting position of the closing tag

:return: (str) Converted data
:since:  v0.1.00
		"""

		raise RuntimeError("Not implemented")
	#

	def _check_match(self, data):
	#
		"""
Check if a possible tag match is a false positive.

:param data: Data starting with the possible tag

:return: (tuple) Matched tag definition; None if false positive
:since:  v0.1.00
		"""

		return None
	#

	def _create_dir(self, dir_path, timeout = -1):
	#
		"""
Creates a directory (or returns the status of is_writable if it exists).
Use slashes - even on Microsoft(R) Windows(R) machines.

:param dir_path: Path to the new directory.
:param timeout: Timeout to use

:return: (bool) True on success
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE
		if (_PY_UNICODE_TYPE != str and type(dir_path) == _PY_UNICODE_TYPE): dir_path = _PY_STR(dir_path, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel._create_dir({0}, {1:d})- (#echo(__LINE__)#)".format(dir_path, timeout))

		dir_path = re.sub("\\/$", "", dir_path)
		dir_path_os = path.normpath(dir_path)

		if (len(dir_path) == 0 or dir_path == "."): _return = False
		elif (path.isdir(dir_path_os) and os.access(dir_path_os, os.W_OK)): _return = True
		elif (path.exists(dir_path_os)): _return = False
		else:
		#
			is_writable = True
			dir_list = dir_path.split("/")
			dir_count = len(dir_list)
			_return = False

			if (timeout < 0): timeout_time = time() + self.timeout_retries
			else: timeout_time = time() + timeout

			if (dir_count > 1):
			#
				dir_list.pop()
				dir_basepath = "/".join(dir_list)
				is_writable = self._create_dir(dir_basepath)
			#

			if (is_writable and time() < timeout_time):
			#
				if (self.umask != None): os.umask(int(self.umask, 8))

				try:
				#
					os.mkdir(dir_path_os, self.chmod_dirs)
					_return = os.access(dir_path_os, os.W_OK)
				#
				except IOError: pass
			#
		#

		return _return
	#

	def _find_end_tag_position(self, data, data_position, tag_end_list):
	#
		"""
Find the starting position of the closing tag.

:param data: String that contains convertable data
:param data_position: Current parser position
:param tag_end_list: List of possible closing tags to be searched for

:return: (int) Position; -1 if not found
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel._find_end_tag_position(data, data_position, tag_end_list)- (#echo(__LINE__)#)")
		_return = None

		is_valid = True
		result = -1

		while ((_return == None or _return > -1) and is_valid):
		#
			for tag_end in tag_end_list:
			#
				result = data.find(tag_end, data_position)
				if (result > -1 and (_return == None or result < _return)): _return = result
			#

			if (_return == None): _return = -1
			elif (_return > -1):
			#
				data_position = _return
				if (data[_return - 1:_return] != "\\"): is_valid = False
			#
		#

		return _return
	#

	def _find_tag_end_position(self, data, data_position, tag_end):
	#
		"""
Find the starting position of the enclosing content.

:param data: String that contains convertable data
:param data_position: Current parser position
:param tag_end: Tag end definition

:return: (int) Position; -1 if not found
:since:  v0.1.00
		"""

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel._find_tag_end_position(data, data_position, tag_end)- (#echo(__LINE__)#)")
		_return = None

		is_valid = True

		while ((_return == None or _return > -1) and is_valid):
		#
			_return = data.find(tag_end, data_position)

			if (_return > -1):
			#
				data_position = _return
				if (data[_return - 1:_return] != "\\"): is_valid = False
			#
		#

		if (_return > -1): _return += len(tag_end)
		return _return
	#

	def _get_variable(self, name):
	#
		"""
Gets the variable content with the given name.

:param name: Variable name

:return: (mixed) Variable content; None if undefined
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE
		if (_PY_UNICODE_TYPE != str and type(name) == _PY_UNICODE_TYPE): name = _PY_STR(name, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel._get_variable({0})- (#echo(__LINE__)#)".format(name))
		return self.parameters.get(name, None)
	#

	def make_all(self):
	#
		"""
Parse and rewrite all directories and files given as include definitions.

:return: (bool) True on success
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE
		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel.make_all()- (#echo(__LINE__)#)")

		_return = False

		if (self.workdir_rescan and len(self.dir_list) > 0 and len(self.filetype_list) > 0):
		#
			self._scan_workdir()
			self.workdir_rescan = False
		#

		if (len(self.file_dict) < 1):
		#
			if (self.event_handler != None): self.event_handler.error("#echo(__FILEPATH__)# -BuilderSkel.make_all()- (#echo(__LINE__)#) reports: No valid files found for parsing")
		#
		else:
		#
			for file_id in self.file_dict:
			#
				_file = self.file_dict[file_id]
				if (_PY_UNICODE_TYPE != str and type(_file) == _PY_UNICODE_TYPE): _file = _PY_STR(_file, "utf-8")

				sys.stdout.write(">>> Processing {0} ... ".format(_file))

				if (self._parse_file(_file)): sys.stdout.write("done\n")
				else: sys.stdout.write("failed\n")
			#
		#

		if (len(self.parser_pickle) > 0):
		#
			sys.stdout.write(">> Writing make.py.pickle\n")

			_file = open(path.normpath(self.parameters['make_pickle_path']
			                           if ("make_pickle_path" in self.parameters) else
			                           "{0}/make.py.pickle".format(self.output_path)
			                          ),
			             "wb"
			            )

			pickle.dump(self.parser_pickle, _file, pickle.HIGHEST_PROTOCOL)
			_file.close()
		#

		return _return
	#

	def _parse(self, parser_tag, data, data_position = 0, nested_tag_end_position = None):
	#
		"""
Parser for "make" tags.

:param parser_tag: Starting tag to be searched for
:param data: Data to be parsed
:param data_position: Current parser position
:param nested_tag_end_position: End position for nested tags

:return: (str) Converted data; None for nested parsing results without a match
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE
		if (_PY_UNICODE_TYPE != str and type(parser_tag) == _PY_UNICODE_TYPE): parser_tag = _PY_STR(parser_tag, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel._parse({0}, data, {1:d}, nested_tag_end_position)- (#echo(__LINE__)#)".format(parser_tag, data_position))

		if (nested_tag_end_position == None):
		#
			data_position = data.find(parser_tag, data_position)
			nested_check = False
		#
		else:
		#
			data_position = data.find(parser_tag, data_position)
			if (data_position >= nested_tag_end_position): data_position = -1

			nested_check = True
			tag_end_position = -1
		#

		while (data_position > -1):
		#
			tag_definition = self._check_match(data[data_position:])

			if (tag_definition == None): data_position += len(parser_tag)
			else:
			#
				tag_length = len(tag_definition[0])
				tag_start_end_position = self._find_tag_end_position(data, data_position + tag_length, tag_definition[1])
				tag_end_position = -1

				if (tag_start_end_position > -1):
				#
					tag_end_position = self._find_end_tag_position(data, tag_start_end_position, tag_definition[2])

					if (tag_end_position < 0): nested_data = None
					else: nested_data = self._parse(parser_tag, data, data_position + 1, tag_end_position)

					while (nested_data != None):
					#
						data = nested_data
						tag_start_end_position = self._find_tag_end_position(data, data_position + 1, tag_definition[1])

						if (tag_start_end_position > -1):
						#
							tag_end_position = self._find_end_tag_position(data,
							                                               tag_start_end_position,
							                                               tag_definition[2]
							                                              )
						#

						nested_data = self._parse(parser_tag, data, data_position + 1, tag_end_position)
					#
				#

				if (tag_end_position > -1):
				#
					data = self._change_match(tag_definition,
					                          data,
					                          data_position,
					                          tag_start_end_position,
					                          tag_end_position
					                         )
				#
				else: data_position += tag_length
			#

			if (nested_check): data_position = -1
			else: data_position = data.find(parser_tag, data_position)
		#

		if (nested_check and tag_end_position < 0): data = None
		return data
	#

	def _parse_data(self, data, file_pathname, file_name):
	#
		"""
Parse the given content.

:param data: Data to be parsed
:param file_pathname: File path
:param file_name: File name

:return: (str) Filtered data
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE
		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel._parse_data(data)- (#echo(__LINE__)#)")

		_return = data.replace("#" + "echo(__FILE__)#", file_name)
		_return = _return.replace("#" + "echo(__FILEPATH__)#", file_pathname)

		if (_return.find("#" + "echo(__LINE__)#") > -1):
		#
			data = re.split("\r\n|\r|\n", _return)
			line = 0

			for result in data:
			#
				data[line] = result.replace("#" + "echo(__LINE__)#", str(line + 1))
				line += 1
			#

			_return = "\n".join(data)
		#

		result_list = re.findall("#" + "echo\\(((?!_)\\w+)\\)#", _return)

		if (len(result_list) > 0):
		#
			matched_list = [ ]

			for result in result_list:
			#
				if (result not in matched_list):
				#
					if (_PY_UNICODE_TYPE != str and type(result) == _PY_UNICODE_TYPE): result = _PY_STR(result, "utf-8")
					value = self._get_variable(result)

					if (value == None): _return = _return.replace("#" + "echo({0})#".format(result), result)
					else: _return = _return.replace("#" + "echo({0})#".format(result), value)

					matched_list.append(result)
				#
			#
		#

		return _return
	#

	def _parse_file(self, file_pathname):
	#
		"""
Handle the given file and call the content parse method.

:param file_pathname: Path to the requested file

:return: (bool) True on success
:since:  v0.1.00
		"""

		# global: _PY_BYTES, _PY_BYTES_TYPE, _PY_STR, _PY_UNICODE_TYPE
		if (_PY_UNICODE_TYPE != str and type(file_pathname) == _PY_UNICODE_TYPE): file_pathname = _PY_STR(file_pathname, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel._parse_file({0})- (#echo(__LINE__)#)".format(file_pathname))

		_return = True

		file_ext = path.splitext(file_pathname)[1][1:]
		file_basename = path.basename(file_pathname)
		file_object = File(self.umask, self.chmod_files, self.timeout_retries, self.event_handler)
		file_text_mode = False

		if (len(file_ext) > 0 and file_ext in self.filetype_ascii_list): file_text_mode = True
		elif (len(file_basename) > 0): file_text_mode = file_basename in self.filetype_ascii_list

		if ((file_text_mode and file_object.open(file_pathname, True, "r"))
		    or file_object.open(file_pathname, True, "rb")
		   ):
		#
			file_content = file_object.read()
			file_object.close()
		#
		else: file_content = None

		file_pathname = re.sub("^{0}".format(re.escape(self.output_strip_prefix)), "", file_pathname)

		if (file_pathname in self.parser_pickle):
		#
			if ((file_text_mode and file_object.open(self.output_path + file_pathname, True, "r"))
			    or file_object.open(self.output_path + file_pathname, True, "rb")
			   ):
			#
				file_old_content = file_object.read()
				file_object.close()

				if (type(file_old_content) != _PY_BYTES_TYPE): file_old_content = _PY_BYTES(file_old_content, "utf-8")
				file_old_content_md5 = hashlib.md5(file_old_content).hexdigest()
			#
			else: file_old_content_md5 = None

			if (file_old_content_md5 != None and file_old_content_md5 != self.parser_pickle[file_pathname]):
			#
				_return = False
				sys.stdout.write("has been changed ... ")
			#
		#

		if (_return):
		#
			if (file_content == None):
			#
				file_content = ""
				_return = self._write_file("", self.output_path + file_pathname)
			#
			elif (file_text_mode):
			#
				file_content = self._parse_data(file_content, file_pathname, file_basename)
				_return = self._write_file(file_content, self.output_path + file_pathname, "w+")
			#
			else: _return = self._write_file(file_content, self.output_path + file_pathname)

			if (type(file_content) != _PY_BYTES_TYPE): file_content = _PY_BYTES(file_content, "utf-8")
			if (_return): self.parser_pickle[file_pathname] = hashlib.md5(file_content).hexdigest()
		#

		return _return
	#

	def _remove_data_dev_comments(self, data):
	#
		"""
Remove all development comments from the content.

:param data: Data to be parsed

:return: (str) Filtered data
:since:  v0.1.00
		"""

		return data
	#

	def _scan_workdir(self):
	#
		"""
Scan given directories for files to be parsed.

:since: v0.1.00
		"""

		# global: _PY_BYTES, _PY_BYTES_TYPE, _PY_STR, _PY_UNICODE_TYPE
		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel._scan_workdir()- (#echo(__LINE__)#)")

		"""
Create a list of files - we need to scan directories recursively ...
		"""

		re_content_estripped = re.compile("^{0}".format(re.escape(self.output_strip_prefix)))
		sys.stdout.write(">> Ready to build file index\n")
		dir_counter = 0

		while (len(self.dir_list) > dir_counter):
		#
			sys.stdout.write(">>> Scanning {0} ... ".format(self.dir_list[dir_counter]))
			dir_path_os = path.normpath(self.dir_list[dir_counter])

			if (path.isdir(dir_path_os) and os.access(dir_path_os, os.R_OK)):
			#
				content_list = os.listdir(dir_path_os)

				for content in content_list:
				#
					if (content[0] != "."):
					#
						if (self.dir_list[dir_counter].endswith("/")): content_extended = self.dir_list[dir_counter] + content
						else: content_extended = "{0}/{1}".format(self.dir_list[dir_counter], content)

						content_extended_os = path.normpath(content_extended)
						content_estripped = re_content_estripped.sub("", content_extended)
						if (_PY_UNICODE_TYPE != str and type(content_estripped) == _PY_UNICODE_TYPE): content_estripped = _PY_STR(content_estripped, "utf-8")

						if (path.isdir(content_extended_os)):
						#
							if ((content not in self.dir_exclude_list)
							    and (content_estripped not in self.dir_exclude_list)
							   ): self.dir_list.append(content_extended)
						#
						elif (path.isfile(content_extended_os)):
						#
							content_ext = path.splitext(content)[1][1:]
							content_id = content_estripped

							if (type(content_id) != _PY_BYTES_TYPE): content_id = _PY_BYTES(content_id, "utf-8")
							content_id = hashlib.md5(content_id).hexdigest()

							if (len(content_ext) > 0
							    and content_ext in self.filetype_list
							    and content not in self.file_exclude_list
							    and content_estripped not in self.file_exclude_list
							   ): self.file_dict[content_id] = content_extended
						#
					#
				#

				sys.stdout.write("done\n")
			#
			else: sys.stdout.write("failed\n")

			dir_counter += 1
		#
	#

	def set_event_handler(self, event_handler = None):
	#
		"""
Sets the EventHandler.

:param event_handler: EventHandler to use

:since: v0.1.00
		"""

		self.event_handler = event_handler
	#

	def set_exclude(self, exclude):
	#
		"""
Add "exclude" definitions for directories and files.

:param exclude: String (delimiter is ",") with exclude names or paths

:since: v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE
		if (_PY_UNICODE_TYPE != str and type(exclude) == _PY_UNICODE_TYPE): exclude = _PY_STR(exclude, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel.set_exclude({0})- (#echo(__LINE__)#)".format(exclude))

		if (type(exclude) == str):
		#
			exclude_list = exclude.split(",")

			for exclude in exclude_list:
			#
				self.dir_exclude_list.append(exclude)
				self.file_exclude_list.append(exclude)
			#
		#
		elif (self.event_handler != None): self.event_handler.warn("#echo(__FILEPATH__)# -BuilderSkel.set_exclude()- (#echo(__LINE__)#) reports: Given parameter is not a string")
	#

	def set_exclude_dirs(self, exclude):
	#
		"""
Add "exclude" definitions for directories.

:param exclude: String (delimiter is ",") with exclude names or paths

:since: v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE
		if (_PY_UNICODE_TYPE != str and type(exclude) == _PY_UNICODE_TYPE): exclude = _PY_STR(exclude, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel.set_exclude_dirs({0})- (#echo(__LINE__)#)".format(exclude))

		if (type(exclude) == str):
		#
			exclude_list = exclude.split(",")
			for exclude in exclude_list: self.dir_exclude_list.append(exclude)
		#
		elif (self.event_handler != None): self.event_handler.warn("#echo(__FILEPATH__)# -BuilderSkel.set_exclude_dirs()- (#echo(__LINE__)#) reports: Given parameter is not a string")
	#

	def set_exclude_files(self, exclude):
	#
		"""
Add "exclude" definitions for files.

:param exclude: String (delimiter is ",") with exclude names or paths

:since: v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE
		if (_PY_UNICODE_TYPE != str and type(exclude) == _PY_UNICODE_TYPE): exclude = _PY_STR(exclude, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel.set_exclude_files({0})- (#echo(__LINE__)#)".format(exclude))

		if (type(exclude) == str):
		#
			exclude_list = exclude.split(",")
			for exclude in exclude_list: self.file_exclude_list.append(exclude)
		#
		elif (self.event_handler != None): self.event_handler.warn("#echo(__FILEPATH__)# -BuilderSkel.set_exclude_files()- (#echo(__LINE__)#) reports: Given parameter is not a string")
	#

	def set_new_target(self, parameters, include, output_path, filetype):
	#
		"""
Sets a new target for processing.

:param parameters: DEFINE statements
:param include: String (delimiter is ",") with directory or file names to
                be included.
:param output_path: Output path
:param filetype: String (delimiter is ",") with extensions of files to be
                 parsed.

:since: v0.1.00
		"""

		# global: _PY_BYTES, _PY_BYTES_TYPE
		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel.set_new_target(parameters, include, output_path, filetype)- (#echo(__LINE__)#)")

		self.dir_exclude_list = [ ]
		self.file_exclude_list = [ ]
		self.filetype_list = filetype.split(",")

		if (len(output_path) > 0
		    and (not output_path.endswith("/"))
		    and (not output_path.endswith("\\"))
		   ): output_path += path.sep

		self.output_path = output_path
		self.output_strip_prefix = ""

		if (type(parameters) == dict): self.parameters = parameters
		else: self.parameters = { }

		sys.stdout.write("> New output target {0}\n".format(output_path))

		make_pickle_path = path.normpath(self.parameters['make_pickle_path']
		                                 if ("make_pickle_path" in self.parameters) else
		                                 "{0}/make.py.pickle".format(output_path)
		                                )

		if (os.access(make_pickle_path, os.W_OK)):
		#
			sys.stdout.write(">> Reading make.py.pickle\n")

			_file = open(make_pickle_path, "rb")
			self.parser_pickle = pickle.load(_file)
			_file.close()
		#
		else: self.parser_pickle = { }

		if (type(self.parser_pickle) != dict): self.parser_pickle = { }

		data_list = include.split(",")

		for data in data_list:
		#
			if (path.isdir(data)):
			#
				if (self.workdir_rescan == False and data not in self.dir_list):
				#
					self.dir_list = [ ]
					self.file_dict = { }
					self.workdir_rescan = True
				#

				self.dir_list.append(data)
			#
			elif (path.isfile(data)):
			#
				if (type(data) != _PY_BYTES_TYPE): data = _PY_BYTES(data, "utf-8")
				file_id = hashlib.md5(data).hexdigest()

				if (self.workdir_rescan == False and file_id not in self.file_dict):
				#
					self.dir_list = [ ]
					self.file_dict = { }
					self.workdir_rescan = True
				#

				self.file_dict[file_id] = data
			#
		#
	#

	def set_strip_prefix(self, strip_prefix):
	#
		"""
Define a prefix to be stripped from output paths.

:param strip_prefix: Prefix definition

:since: v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE
		if (_PY_UNICODE_TYPE != str and type(strip_prefix) == _PY_UNICODE_TYPE): strip_prefix = _PY_STR(strip_prefix, "utf-8")

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel.set_strip_prefix({0})- (#echo(__LINE__)#)".format(strip_prefix))

		if (type(strip_prefix) == str): self.output_strip_prefix = strip_prefix
		elif (self.event_handler != None): self.event_handler.warn("#echo(__FILEPATH__)# -BuilderSkel.set_strip_prefix()- (#echo(__LINE__)#) reports: Given parameter is not a string")
	#

	def _write_file(self, file_content, file_pathname, file_mode = "w+b"):
	#
		"""
Write the given file to the defined location. Create subdirectories if
needed.

:param file_content: Parsed content
:param file_pathname: Path to the output file
:param file_mode: Filemode to use

:return: (bool) True on success
:since:  v0.1.00
		"""

		# global: _PY_STR, _PY_UNICODE_TYPE
		if (_PY_UNICODE_TYPE != str):
		#
			if (type(file_pathname) == _PY_UNICODE_TYPE): file_pathname = _PY_STR(file_pathname, "utf-8")
			if (type(file_mode) == _PY_UNICODE_TYPE): file_mode = _PY_STR(file_mode, "utf-8")
		#

		if (self.event_handler != None): self.event_handler.debug("#echo(__FILEPATH__)# -BuilderSkel._write_file(file_content, {0}, {1})- (#echo(__LINE__)#)".format(file_pathname, file_mode))

		dir_path = path.dirname(file_pathname)
		_return = False

		if (len(dir_path) < 1 or self._create_dir(dir_path)):
		#
			file_object = File(self.umask, self.chmod_files, self.timeout_retries, self.event_handler)

			if (file_object.open(file_pathname, False, file_mode)):
			#
				_return = file_object.write(file_content)
				file_object.close()
			#
		#

		return _return
	#
#

##j## EOF