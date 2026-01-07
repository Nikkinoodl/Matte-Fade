#!/usr/bin/env python
# -*- coding: utf8 -*-

from gimpfu import *

def mattefade( img, draw, useColor, colorScheme, orientation, flipColors, colorOpacity, colorOffset, overExposure, oeAmount, addVignette, sharpAmount):
	
	current_f=pdb.gimp_context_get_foreground()
	current_b=pdb.gimp_context_get_background()

	#clean start
	img.disable_undo()
	pdb.gimp_context_push()

	#get height and width
	pdb.gimp_selection_all
	sel_size=pdb.gimp_selection_bounds(img)
	w=sel_size[3]-sel_size[1]
	h=sel_size[4]-sel_size[2]

	if orientation == 0:
		#vertical gradient
		#set color gradient start point
		startX = w/2
		startY = 0
	
		#set color gradient end points
		endX = w/2
		endY = h

	else:
		#horizontal gradient
		#set color gradient start point
		startX = 0
		startY = h/2
	
		#set color gradient end points
		endX = w
		endY = h/2

	#set image center and corner points
	centerX = w/2
	centerY = h/2
	cornerX = w
	cornerY = h

	###
	### Adjust curves
	###

	#layer copy from background and use this as the starting point for processing
	copyLayer1=pdb.gimp_layer_new_from_visible(img, img, "AdjustCurves")
	pdb.gimp_image_insert_layer(img, copyLayer1, None, -1)

	#adjust curves
	curveArray = [0, 0.22846441947565543, 0.28650137741046827, 0.348314606741573, 1, 1]
	pdb.gimp_drawable_curves_spline(copyLayer1, HISTOGRAM_VALUE, 6, curveArray)


	###
	### Add sharpening
	###

	if sharpAmount > 0:

		#set other contexts for sharpen gradient.
		pdb.gimp_context_set_opacity(70)
		pdb.gimp_context_set_paint_mode(LAYER_MODE_NORMAL)
		pdb.gimp_context_set_gradient_fg_bg_rgb()
		pdb.gimp_context_set_gradient_blend_color_space(1)
		pdb.gimp_context_set_gradient_reverse(FALSE)

		#set colors to black and white
		pdb.gimp_context_set_foreground((255, 255, 255))
		pdb.gimp_context_set_background((0, 0, 0))

		#copy the visible image for sharpening
		copyLayer6=pdb.gimp_layer_new_from_visible(img, img, "Sharpen")
		pdb.gimp_image_insert_layer(img, copyLayer6, None, -1)

		#unsharp mask settings
		sharpRadius = 2
		sharpThreshold = 0
		sharpOffset = 50

		#add unsharp mask
		pdb.plug_in_unsharp_mask(img, copyLayer6, sharpRadius, sharpAmount, sharpThreshold)

		#add layer mask with black fill 
		layerMask6 = copyLayer6.create_mask(1)
		copyLayer6.add_mask(layerMask6)

		#apply a blend to the layer mask that fades out sharpening away from the center of the image
		pdb.gimp_drawable_edit_gradient_fill(layerMask6, 2, sharpOffset, FALSE, 1, 0, TRUE, centerX, centerY, cornerX, cornerY)

	###
	### Add vignette
	###

	if addVignette == TRUE:

		#set other contexts for vignette gradient.
		pdb.gimp_context_set_opacity(35)
		pdb.gimp_context_set_paint_mode(LAYER_MODE_NORMAL)
		pdb.gimp_context_set_gradient_fg_transparent()
		pdb.gimp_context_set_gradient_blend_color_space(1)
		pdb.gimp_context_set_gradient_reverse(TRUE)

		#set foreground color
		pdb.gimp_context_set_foreground((0, 0, 0))

		#add a new layer for vignette
		copyLayer5=pdb.gimp_layer_new(img, w, h, 1, "Vignette", 100.0, 23)
		pdb.gimp_image_insert_layer(img, copyLayer5, None, -2)
		pdb.gimp_drawable_fill(copyLayer5, 3)

		#add radial gradient w/start point in center of image
		vignetteOffset = 80
		pdb.gimp_drawable_edit_gradient_fill(copyLayer5, 2, vignetteOffset, FALSE, 1, 0, TRUE, centerX, centerY, cornerX, cornerY)


	###
	### Add color overlay
	###

	if useColor == TRUE:

		#set contexts for gradient
		pdb.gimp_context_set_opacity(colorOpacity)
		pdb.gimp_context_set_paint_mode(LAYER_MODE_ADDITION)
		pdb.gimp_context_set_gradient_fg_bg_rgb()
		pdb.gimp_context_set_gradient_blend_color_space(1)
		pdb.gimp_context_set_gradient_reverse(flipColors)

		#set color contexts
		if colorScheme == 0:
			#warm colors to violet and orange
			pdb.gimp_context_set_foreground((198, 4, 198))
			pdb.gimp_context_set_background((227, 145, 3))
		elif colorScheme == 1:
			#cool colors to purple and teal
			pdb.gimp_context_set_foreground((124, 63, 156))
			pdb.gimp_context_set_background((10, 139, 166))
		elif colorScheme == 2:
			#neutral colors to purple and neutral gray
			pdb.gimp_context_set_foreground((162, 77, 189))
			pdb.gimp_context_set_background((189, 181, 149))
		elif colorScheme == 3:
			#green to transparent
			pdb.gimp_context_set_gradient_fg_transparent()
			pdb.gimp_context_set_foreground((16, 230, 3))
		elif colorScheme == 4:
			#bright orange to transparent
			pdb.gimp_context_set_gradient_fg_transparent()
			pdb.gimp_context_set_foreground((236, 180, 102))
		else:
			#dark orange to transparent
			pdb.gimp_context_set_gradient_fg_transparent()
			pdb.gimp_context_set_foreground((178, 77, 0))

		#create new layer and fill with transparency
		copyLayer2=pdb.gimp_layer_new(img, w, h, 1, "ColorScreen", 100.0, 23)
		pdb.gimp_image_insert_layer(img, copyLayer2, None, -1)
		pdb.gimp_drawable_fill(copyLayer2, 3)

		#add gradient w/start point in top center of image finish in bottom center
		pdb.gimp_drawable_edit_gradient_fill(copyLayer2, 0, colorOffset, FALSE, 1, 0, TRUE, startX, startY, endX, endY )

	###
	### Add overexposure
	###

	if overExposure == TRUE:
	
		#set other contexts for overexposure gradient.
		pdb.gimp_context_set_opacity(oeAmount)
		pdb.gimp_context_set_paint_mode(LAYER_MODE_ADDITION)
		pdb.gimp_context_set_gradient_fg_transparent()
		pdb.gimp_context_set_gradient_blend_color_space(1)
		pdb.gimp_context_set_gradient_reverse(FALSE)

		#set colors to white and black
		pdb.gimp_context_set_foreground((255, 255, 255))
		pdb.gimp_context_set_background((0, 0, 0))
	
		#set gradient offset to fixed amount
		oeOffset = 0

		copyLayer4=pdb.gimp_layer_new(img, w, h, 1, "OverExposure", 100.0, 23)
		pdb.gimp_image_insert_layer(img, copyLayer4, None, -1)
		pdb.gimp_drawable_fill(copyLayer4, 3)

		#add radial gradient w/start point in center of image finish in bottom center or center right edge
		pdb.gimp_drawable_edit_gradient_fill(copyLayer4, 2, oeOffset, FALSE, 1, 0, TRUE, centerX, centerY, endX, endY )

	#clean up	
	pdb.gimp_displays_flush()
	pdb.gimp_context_pop()
	img.enable_undo()
	pdb.gimp_context_set_foreground(current_f)
	pdb.gimp_context_set_background(current_b)


register( "gimp_matte_fade",
  "Add matte faded effect",
  "Add matte faded effect",
  "Simon Bland",
  "(©) 2023 Simon Bland",
  "2023-01-25",
  "<Image>/Filters/Matte Fade",
  'RGB*',
  [
	(PF_TOGGLE, "useColor", "Use colors", 1),
	(PF_OPTION, "colorScheme", "	Color scheme", 0, (['Violet/Yellow', 'Purple/Teal', 'Purple/Neutral' , 'Green/Transp.', 'Br.Orange/Transp.', 'Dk.Orange/Transp.'])),
	(PF_OPTION, "orientation", "	Orientation", 0, (['Vertical', 'Horizontal'])),
	(PF_TOGGLE, "flipColors", "	Flip colors", 0),
	(PF_SLIDER, "colorOpacity", "	Opacity", 25, (0, 100, 5)),
	(PF_SLIDER, "colorOffset", "	Offset", 20, (0, 100, 5)),
	(PF_TOGGLE, "overExposure", "Over expose", 1),
	(PF_SLIDER, "oeAmount", "	Over exposure amt", 20, (0, 100, 5)),
	(PF_TOGGLE, "addVignette", "Add vignette", 1),
	(PF_SLIDER, "sharpAmount", "Sharpen amount", 1.0, (0, 5.0, 0.1))
  ],
  '',
  mattefade)

main()

