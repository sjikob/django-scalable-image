# -*- coding: UTF-8 -*

import os.path
from PIL import Image
import logging

try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

from django.db              import models
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist


class ScaledPicture(models.Model):

	# Can be overridden in sub-classes
	IMAGE_OPTIONS = {}

	class Meta:
		abstract = True

	size    = models.PositiveIntegerField()
	file    = models.ImageField(upload_to='pictures/scaled', **IMAGE_OPTIONS)
	cr_date = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return u"%s [%spx]" % \
			(self.parent, self.size)


class ScalableImage(object):

	def __init__(self, *args, **kwargs):
		assert issubclass(self.SCALED_MODEL, ScaledPicture), \
			'SCALED_MODEL must be a sub-class of ScaledPicture'
		super(ScalableImage, self).__init__(*args, **kwargs)

	def get_image_ratio(self, size):
		"""
		When supplied with an image "size" (in pixels), returns a tuple of
		x / y dimensions that will scale the image to fit in a box of <size> ×
		<size> pixels while keeping the aspect ratio of the original image.
		"""
	
		orig_width  = self.file.width
		orig_height = self.file.height
	
		if orig_width > orig_height:
			ratio  = float(orig_height) / orig_width
			width  = size
			height = int(size * ratio)
	
		elif orig_width < orig_height:
			ratio  = float(orig_width) / orig_height
			width  = int(size * ratio)
			height = size
	
		else:
			width = height = size

		return (width, height)

	def get_tiny_picture(self):
		"""
		Returns a new SCALED_MODEL object of maximum size 64×64
		"""
		return self.get_scaled_picture(64)

	def get_small_picture(self):
		"""
		Returns a new SCALED_MODEL object of maximum size 128×128
		"""
		return self.get_scaled_picture(128)

	def get_large_picture(self):
		"""
		Returns a new SCALED_MODEL object of maximum size 256×256
		"""
		return self.get_scaled_picture(256)

	def get_huge_picture(self):
		"""
		Returns a new SCALED_MODEL object of maximum size 384×384
		"""
		return self.get_scaled_picture(384)

	def get_scaled_picture(self, size):
		"""
		Returns a new SCALED_MODEL of arbitrary size, indicated by [size]
		argument.
		"""

		try:
			scaled_picture = self.SCALED_MODEL.objects.get(
				parent = self,
				size   = size,
			)

			if scaled_picture.cr_date < self.cr_date:
				logging.info(
					"Parent picture has been replaced since this scaled picture "
					"was created, regenerating..."
				)
				scaled_picture.delete()
				raise ObjectDoesNotExist()

			if scaled_picture.file.url == None:
				logging.info(
					"Parent picture has no URL, possibly it doesn't exist"
				)
				scaled_picture.delete()
				raise ObjectDoesNotExist()

			# Return as-is
			return scaled_picture

		except ObjectDoesNotExist:
			pass

		# We need to create a new object of the requested size.
		# Note that the "file" attribute won't yet be populated.
		scaled_picture = self.SCALED_MODEL(
			parent = self,
			size   = size,
		)

		# Load the image from this object into a PIL Image object and
		# manipulate
		try:
			img = Image.open(self.file)
		except Exception, e:
			logging.warning("Exception opening file %s: %s", self.file, e)
			return None

		width, height = self.get_image_ratio(size)

		new_img = img.resize( (width, height), Image.ANTIALIAS)

		new_name = "__%ix%i__.%s.jpg" % (
			width,
			height,
			os.path.basename(self.file.name),
		)

		# Need to provide a File-like object to the file field
		# of the scaled picture containing the image data
		io = StringIO()
		new_img.save(io, 'JPEG', quality=90)
		new_img_file = ContentFile(io.getvalue())

		scaled_picture.file.save(
			name=new_name,
			content=new_img_file,
		)

		scaled_picture.save()

		return scaled_picture


class Picture(models.Model, ScalableImage):

	# Can be overridden in sub-classes
	IMAGE_OPTIONS = {}

	class Meta:
		abstract = True

	file    = models.ImageField(upload_to='pictures', **IMAGE_OPTIONS)
	cr_date = models.DateTimeField(auto_now=True)

