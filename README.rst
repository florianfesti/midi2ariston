# Midi 2 Ariston

Midi2ariston is a small tool for converting midi music to punch tape,
cards or discs for mechanical music instruments as Ariston organettes
(which gives the tool its name as it was the first instrument
supported), music boxes and street organs.

Midi2Ariston is implemented in Python using the cairo library to
produce SVG graphics that can be turned into physical media using a
laser cutter ot cutting plotter.

While it is still pretty fresh it already supports checking for
pitches not playable by the target instrument and tones not playable
due to being too close together (a problem common to music boxes which
probe the punch tape with sproket wheel).

For now there are only 3 instruments that are actually tested:

* Ariston organette (Ariston)
* 20 note music box (Pling20)
* 30 note music box (Pling30)

There are a couple of still to be tested instruments - most of them
punch tape street organs.

Other instruments can be added easily. New kind of output media can be
added by implementing a new class in
instruments/__init__.py. For instruments similar to already existing ones
just copy their file in instruments/ and adjust the details like
supported pitches and the measurements of the tracks.
