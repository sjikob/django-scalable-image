# django-scalable-image

A set of django abstract classes for defining images and auto-generating scaled
versions (based on supplied pixel size).

### Example definition of "picture" class and "scalable picture"
```
import scalable_image

...

class ScaledProductPhoto(ScaledPicture):
	parent = models.ForeignKey('ProductPhoto')

class ProductPhoto(Picture):

	# Specify the class of the "scaled" photo to return when requested.
	SCALED_MODEL = ScaledProductPhoto

	# If you're linking your photos with specific external objects
	parent = models.ForeignKey('Product')

	# Any additional django model fields
	# ...

```

Calls to `ProductPhoto.get_scaled_picture(pixels)` will return a
`ScaledProductPhoto` instance of the specified size (keeping aspect). If the
specified size of picture has never been requested then the original image will
be scaled, saved to the django storage and then returned. If previously
requested then the image is returned directly from storage.

The image file can be accessed via `ProductPhoto.file` or
`ScaledProductPhoto.file`.

As well as `get_scaled_picture` there are several method for pre-defined image
sizes, listed in the example below, or you can create your own methods for your
standardised image sizes on the `ProductPhoto` sub-class.

### Example use in template player
```

<table>
	<tr>
		<th>64 pixels</th>
		<td>{{ picture.get_tiny_picture.file.url }}</td>
	</tr>
	<tr>
		<th>128 pixels</th>
		<td>{{ picture.get_small_picture.file.url }}</td>
	</tr>
	<tr>
		<th>256 pixels</th>
		<td>{{ picture.get_large_picture.file.url }}</td>
	</tr>
	<tr>
		<th>384 pixels</th>
		<td>{{ picture.get_huge_picture.file.url }}</td>
	</tr>
</table>
```
