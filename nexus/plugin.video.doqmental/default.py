# -*- coding: utf-8 -*-
#------------------------------------------------------------
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code from youtube addon
#------------------------------------------------------------

import os
import sys
import plugintools
import xbmc,xbmcaddon


addonID = 'plugin.video.doqmental'

local = xbmcaddon.Addon(id=addonID)
icon = local.getAddonInfo('icon')

YOUTUBE_CHANNEL_ID1 = "UCrqe-XBFY33iif8qU0QVBfQ"
YOUTUBE_CHANNEL_ID2 = "UC0QO3TaHg14sRc3pPFmaXnQ"
YOUTUBE_CHANNEL_ID3 = "UC0gJz-PAVJhPnDwkc4oATVw"
YOUTUBE_CHANNEL_ID4 = "UCJCen5xxTtU7cnVHe3n424A"
YOUTUBE_CHANNEL_ID5 = "UCfjYH7g7LHEQa02UDu1uERA"
YOUTUBE_CHANNEL_ID6 = "UCwPM0OD-ILlnzGnm-JOoRlg"
YOUTUBE_CHANNEL_ID7 = "UCaXupcZvG8NMZwbFO4vh4Tg"
YOUTUBE_CHANNEL_ID8 = "UCUxNfoV8i3NQAAwIVk7LwVQ"
YOUTUBE_CHANNEL_ID9 = "UCQ1GpKa15ulyoQuxz7H4rng"
YOUTUBE_CHANNEL_ID10 = "UC8oUl46VlJTJvLQ_2oIkv-g"
YOUTUBE_CHANNEL_ID11 = "UCtIhP9xqkrNX7CT2vD6pD7Q"
YOUTUBE_CHANNEL_ID12 = "UC7nlDZFrAs16q0ni9T4m6sw"
YOUTUBE_CHANNEL_ID13 = "UCv05qOuJ6Igbe-EyQibJgwQ"


# Entry point
def run():
    plugintools.log("doqmental.run")
    
    # Get params
    params = plugintools.get_params()
    
    if params.get("action") is None:
        main_list(params)
    else:
        pass
    
    plugintools.close_item_list()

# Main menu
def main_list(params):
    plugintools.log("doqmental.main_list "+repr(params))

	
     
   
 
    plugintools.add_item( 
        #action="", 
        title="Documentales ESP",
        url="plugin://plugin.video.youtube/playlist/PLGH_5Dpd62t3hALRGkPf7DsVb86jflqBZ/",
        thumbnail="https://1.bp.blogspot.com/-dlS1ODVF4Uw/YKP-VUjZMuI/AAAAAAABs6g/FbGqK194sp8onOc0j5qPnfUiV3sX6s7SQCLcBGAsYHQ/s529/daniel-tong-xBeid9r1paU-unsplash%2B%25281%2529.jpg",
        fanart="https://1.bp.blogspot.com/-TqcgJeTt2Yw/YKP-boROVSI/AAAAAAABs6k/Ps3HAfcl_HQH3bZ1fWK-PpOXTCbH9c1ngCLcBGAsYHQ/s1920/giammarco-zeH-ljawHtg-unsplash.jpg",
        folder=True )


 
    plugintools.add_item( 
        #action="", 
        title="Borisland",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID1+"/",
        thumbnail="https://1.bp.blogspot.com/-Q-az5WorSx4/YKKLzArKn4I/AAAAAAABs4w/R2xJzZbDcgwCJSgsaILdiQdTJ_IbjAAfwCLcBGAsYHQ/s900/unnamed.jpg",
		fanart="https://1.bp.blogspot.com/-piQo6wAYXdI/YKKLYuVmoII/AAAAAAABs4o/M0BVKhk4t5wjzQdedJ9f0e5qMR8t9T06ACLcBGAsYHQ/s1920/bailey-zindel-NRQV-hBF10M-unsplash.jpg",
        folder=True )     
        
    plugintools.add_item( 
        #action="", 
        title="Lethal Crysis",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID4+"/",
        thumbnail="https://1.bp.blogspot.com/-YgbRGkUPIkk/YKPv3e44x3I/AAAAAAABs5E/wBK35zRhwIc3v_U1Gg81H8zB58eFIE5yQCLcBGAsYHQ/s802/icon.jpg",
        fanart="https://1.bp.blogspot.com/-mW0Ub3CWgl8/YKPvv45NXuI/AAAAAAABs5A/B5098cWDV3gQZXWOqkMrP_E60Hp99AC5ACLcBGAsYHQ/s1280/EZh45pKWkAcEqlT.jpg",
        folder=True )
        
       
    plugintools.add_item( 
        #action="", 
        title="Rubén Villalobos",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID2+"/",
        thumbnail="https://1.bp.blogspot.com/-PM45NLHVqBw/YKPz656_K4I/AAAAAAABs5g/iA8feIg5bgMNiUB1qvFBRKmFvwKrm7-uQCLcBGAsYHQ/s900/unnamed%2B%25282%2529.jpg",
        fanart="https://1.bp.blogspot.com/-7xxLs0WGnDQ/YKPzydNuA0I/AAAAAAABs5c/fa-bo2-Wd8UJWebYhJvln6mXALkfez0XQCLcBGAsYHQ/s1920/aussieactive-oTRD-P4nU8Q-unsplash.jpg",
        folder=True )    
  
    plugintools.add_item( 
        #action="", 
        title="Planeta Salvaje",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID5+"/",
        thumbnail="https://1.bp.blogspot.com/-TQoSKHPVY8g/YKPwTcB5djI/AAAAAAABs5M/N6Owb-kxFKgjkwTRF8tP_1RHBURzZ27wACLcBGAsYHQ/s900/unnamed%2B%25281%2529.jpg",
        fanart="https://1.bp.blogspot.com/-YgBD0TXydaA/YKPyB_d0S1I/AAAAAAABs5U/63gXTSXvG40cTwEwzMDQvXTCGDxZZ3fKQCLcBGAsYHQ/s1920/kalen-emsley-Bkci_8qcdvQ-unsplash.jpg",
        folder=True )  
        
           
           
    plugintools.add_item( 
        #action="", 
        title="Secretos de la Historia",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID3+"/",
        thumbnail="https://1.bp.blogspot.com/-qVKt1Qu2MuQ/YKP2WbKTHHI/AAAAAAABs5s/7HKeweicr9kiE6DP9SFm4P4oIf28lADTgCLcBGAsYHQ/s900/unnamed%2B%25283%2529.jpg",
        fanart="https://1.bp.blogspot.com/-q1QGyYBzvE8/YKP3aWA88JI/AAAAAAABs50/IVqAIEcdzfYBzTrczWTswebBgKZqkSPnQCLcBGAsYHQ/s1920/ken-cheung-KonWFWUaAuk-unsplash.jpg",
        folder=True )    
        
                   
    plugintools.add_item( 
        #action="", 
        title="Sever Documentales",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID6+"/",
        thumbnail="https://1.bp.blogspot.com/-8sMBd8WeAtM/YKP5a10QydI/AAAAAAABs6E/sH8c4TdOfZUbzx0Of9wjeOs6w8y3n61EwCLcBGAsYHQ/s900/unnamed%2B%25284%2529.jpg",
        fanart="https://1.bp.blogspot.com/-I3rf6DBsmew/YKP5Q6DvAsI/AAAAAAABs58/Wl19C0WAlRc35CJHhQhFmNGaxNyfv9igQCLcBGAsYHQ/s1920/shot-by-cerqueira-0o_GEzyargo-unsplash.jpg",
        folder=True ) 
    
    
    plugintools.add_item( 
        #action="", 
        title="Misterios Ocultos",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID7+"/",
        thumbnail="https://1.bp.blogspot.com/-EXX99ypIUo0/YKP7Q-Xx2aI/AAAAAAABs6U/FtV_s_2EGEgFitNC-ZZSs1XPRtkkK8PxACLcBGAsYHQ/s900/unnamed%2B%25285%2529.jpg",
        fanart="https://1.bp.blogspot.com/-SVgn9sffdrs/YKP7KgVyH_I/AAAAAAABs6Q/g6JrjjTo1Cwfb7xWuS7DFiEo-Mwgh3TowCLcBGAsYHQ/s1280/maxresdefault.jpg",
        folder=True ) 
            
            
    plugintools.add_item( 
        #action="", 
        title="Aprende con Documentales",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID8+"/",
        thumbnail="https://1.bp.blogspot.com/-M4oxorsM6Tg/YKQAxG5kT4I/AAAAAAABs6w/hb8Jq5VSFhcdrLXyH7elkOri7kSJkREFwCLcBGAsYHQ/s646/louis-maniquet-71QXQUSC_Do-unsplash.jpg",
        fanart="https://1.bp.blogspot.com/-o13XJDHn_WA/YKQApav223I/AAAAAAABs6s/Bw3XRZH9HoMpdb9FMC37oeFJRY7hc721QCLcBGAsYHQ/s1920/actionvance-t7EL2iG3jMc-unsplash.jpg",
        folder=True )         

    plugintools.add_item( 
        #action="", 
        title="DW Documental",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID9+"/",
        thumbnail="https://1.bp.blogspot.com/-wRK6k6XTNTo/YKQDNkHLvhI/AAAAAAABs7A/BtcXQgKsiKsw8-MhyEdN7L4X2LcSyCSqQCLcBGAsYHQ/s900/unnamed%2B%25286%2529.jpg",
        fanart="https://1.bp.blogspot.com/-px579CXQ2p0/YKQDGscbYXI/AAAAAAABs68/-UzP_ltdH-0W10ETkxrZFAUCME6v2PoWACLcBGAsYHQ/s1200/importancia-de-los-iconos-en-la-creacion-de-paginas-web.jpg",
        folder=True )             
   
   
    plugintools.add_item( 
        #action="", 
        title="Documental Channel Spain",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID10+"/",
        thumbnail="https://1.bp.blogspot.com/-FH-C_cyRuFI/YKY89zNh_yI/AAAAAAABs7c/ScM8qS4a6C0bAMTVg0sHFQ7X8R-4jSlwwCLcBGAsYHQ/s900/unnamed%2B%25287%2529.jpg",
        fanart="https://1.bp.blogspot.com/--Hwf-YgzV5M/YKY8dhCUABI/AAAAAAABs7U/XJ4HteAEQWg0VvinZ6jvexWQyE3CbScgQCLcBGAsYHQ/s1920/ronda-darby-HbMLSB-uhQY-unsplash.jpg",
        folder=True )  
        

    plugintools.add_item( 
        #action="", 
        title="Documania TV",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID11+"/",
        thumbnail="https://1.bp.blogspot.com/-8nyP_CBg0fo/YKZ0qadACxI/AAAAAAABs7o/TPRsmvrxSxkEy4gdIEU_GxCsoB2vASVyQCLcBGAsYHQ/s633/history-in-hd-e5eDHbmHprg-unsplash.jpg",
        fanart="https://1.bp.blogspot.com/-0ecnBpV9cMU/YKZ0ksrvq-I/AAAAAAABs7k/YVRBCuXh3pA_K4ArBWqnb3oubzn8MlhtwCLcBGAsYHQ/s1920/david-kohler-VFRTXGw1VjU-unsplash.jpg",
        folder=True )  

 
    plugintools.add_item( 
        #action="", 
        title="Academia Play",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID13+"/",
        thumbnail="https://1.bp.blogspot.com/-eGN8kls3K-A/YKkScvIZoUI/AAAAAAABs8M/6ehj40XnpDIqadkJaePguXbl7yPxhTJogCLcBGAsYHQ/s225/descarga.jpg",
        fanart="https://1.bp.blogspot.com/-RRy1vV1G-3U/YKkSljD_g2I/AAAAAAABs8Q/iOUS7IrID7MF_9zjZPJVwIqWtNEYtYNDACLcBGAsYHQ/s1280/maxresdefault%2B%25281%2529.jpg",
        folder=True ) 
        
    plugintools.add_item( 
        #action="", 
        title="Planeta Histórico",
        url="plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID12+"/",
        thumbnail="https://1.bp.blogspot.com/-YAK5Sry80jA/YKkT5E6CIUI/AAAAAAABs8c/IPlNcXxLYCcBrpDjhdh_NhOuaR0xuh_5gCLcBGAsYHQ/s900/unnamed%2B%25288%2529.jpg",
        fanart="https://1.bp.blogspot.com/-iC9v8AH0eJg/YKkUNQ_rwyI/AAAAAAABs8k/md1Pv0iaa8kEpi2t6Mv4T6lPHhhSuPzjwCLcBGAsYHQ/s1365/Tierra_planeta.jpg",
        folder=True ) 

        
        
        
run()