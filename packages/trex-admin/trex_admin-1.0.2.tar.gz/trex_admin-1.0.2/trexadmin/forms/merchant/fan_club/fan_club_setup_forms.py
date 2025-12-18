'''
Created on 8 Jan 2024

@author: jacklok
'''
from wtforms import StringField, validators
from trexlib.forms.base_forms import ValidationBaseForm

class FanClubSetupForm(ValidationBaseForm):
    fan_club_setup_key            = StringField('Setup Key')
    
    group_name                    = StringField('Group Name',[
                                                validators.DataRequired(message="Group Name is required"),
                                                validators.Length(max=100, message="Group Name length must not more than 100 characters")
                                            ])
    
    desc                          = StringField('Description',[
                                                validators.DataRequired(message="Description is required"),
                                                validators.Length(max=500, message="Description length must not more than 500 characters")
                                            ])
    
    fan_club_type                 = StringField('Fan Club Type',[
                                                validators.DataRequired(message="Fan Club type is required"),
                                            ])
    
    invite_link                   = StringField('Invite Link',[
                                                validators.DataRequired(message="Invite Link is required"),
                                                validators.Length(max=100, message="Invite Link length must not more than 100 characters")
                                            ])
    
    assign_outlet_key             = StringField('Assign Outlet',[
                                                validators.DataRequired(message="Assign outlet is required"),
                                                
                                            ])
    
    