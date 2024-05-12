# -*- coding: utf-8 -*-

# edit 2023-04-04

if __name__ == "__main__":
	import sys, xbmc
	from resources.lib import utils, vjlive, vjackson
	if utils.PY2:
		if not xbmc.getCondVisibility("System.HasAddon(script.module.futures)"):
			xbmc.executebuiltin('InstallAddon(script.module.futures)')
			xbmc.executebuiltin('SendClick(11)')
	else:
		if not xbmc.getCondVisibility("System.HasAddon(script.module.infotagger)"):
			xbmc.executebuiltin('InstallAddon(script.module.infotagger)')
			xbmc.executebuiltin('SendClick(11)')
		if not xbmc.getCondVisibility("System.HasAddon(inputstream.ffmpegdirect)"):
			xbmc.executebuiltin('InstallAddon(inputstream.ffmpegdirect)')
			xbmc.executebuiltin('SendClick(11)')
		
	params = dict(utils.parse_qsl(sys.argv[2][1:]))
	tv = params.get("name")
	action = params.pop("action", None)
	if tv:
		if action == "addTvFavorit": vjlive.change_favorit(tv)
		elif action == "delTvFavorit": vjlive.change_favorit(tv, True)
		else: vjlive.livePlay(tv)
	elif action == None: vjackson._index(params)
	elif action == "choose": vjlive.choose()
	elif action == "clear": utils.clear()
	elif action == "delete_search": utils.delete_search(params)
	elif action == "delallTvFavorit":
		utils.addon.setSetting("favs", "[]")
		xbmc.executebuiltin('Container.Refresh')
	elif action == "channels": vjlive.channels()
	elif action == "settings": utils.addon.openSettings(sys.argv[1])
	elif action == "favchannels": vjlive.favchannels()
	else: getattr(vjackson, "_%s" % action)(params)