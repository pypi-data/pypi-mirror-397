'''
Created on 5 Jan 2024

@author: jacklok
'''

from flask_babel import gettext
from trexconf import conf

instant_messaing_setup_menu_item = {
                                    'title'         : gettext('Fan Group Setup'),
                                    'menu_item'     : 'manage_fan_club',
                                    'end_point'     : 'fan_club_setup_bp.manage_fan_club_setup',
                                    'icon_class'    : 'fas fa-cog',
                                    'permission'    : 'manage_fan_club',
                        
                        }


menu_items_list  = [
                    instant_messaing_setup_menu_item,
    
                    ]

menu_items = {
                                    'title'         : gettext('Fan Group'),
                                    'menu_item'     : 'marketing',
                                    'icon_class'    : 'fas fa-group',
                                    'permission'    : 'marketing',
                                    'childs'        : menu_items_list
                        
                        }