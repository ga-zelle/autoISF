#
#var round_basal = require('../round-basal')
import sys
import time
from datetime import datetime
from email.utils import formatdate
import math
import copy
#import matplotlib.pyplot as plt
#import setTempBasal as tempBasalFunctions

def round_basal(value, dummy) :
    # copied to setTempBasal, too !!!
    # initially fixed
    #return round(value, 2)
    
    # Rounds value to 'digits' decimal places
    #function round(value, digits):
    #    if (! digits) { digits = 0; }
    #    var scale = Math.pow(10, digits);
    return round(value, 4)                  # make it compatible with logfile format


#// we expect BG to rise or fall at the rate of BGI,
#// adjusted by the rate at which BG would need to rise /
#// fall to get eventualBG to target over 2 hours
def calculate_expected_delta(target_bg, eventual_bg, bgi):
    #// (hours * mins_per_hour) / 5 = how many 5 minute periods in 2h = 24
    five_min_blocks = (2 * 60) / 5
    target_delta = target_bg - eventual_bg
    expectedDelta = round(bgi + (target_delta / five_min_blocks), 1)
    return expectedDelta

def convert_bg(value, profile):
    # while testing all is in mg/dl
    return round(value)

def typeof(thing, *arg):
    # copied to setTempBasal, too !!!
    element = 'typeof'          # the default
    for a in arg:               # argument(s) beyong thing
        element = a             # keep last argument as given sub-element

    if element in thing:
        return 'defined'
    else:
        return 'undefined'

def my_ce_file(filnam) :
    ### added to get and hold the name of the console.error filename
    global ce_file
    ce_file = filnam
    
def console_error(sb, *argstr):
    #   concatenate arguments by inserting single BLANK
    #   also, enforce all later arguments to be string type
    for st in argstr:
        sb += ' ' + str(st)
    sb_quoted = sb.replace("'", '"')                # change single quoted into double quote
    sb_colon = sb_quoted.replace('": ', '":')       # erase BLANK after colon
    sb_comma = sb_colon.replace(', "', ',"')        # erase BLANK before next keyword
    sb_curly = sb_comma.replace(':{', ': {')        # insert BLANK before json object
    
    #log = open('C:\gazelle\Dokumente\BZ\Looping\PID\console_error.log', 'a')
    log = open(ce_file, 'a')
    log.write(sb_curly + '\n')
    #print (sb)
    log.close()

def joinCIs(listCIs):
    # extract list elements and append to string, separated by BLANKS
    # emulates the jave join instruction
    ls = ''
    for ele in range(len(listCIs)):
        ls += ' ' + str(round(listCIs[ele], 0))
    return ls

def short(num):
    # emulate apparent java formating if num effectively has no decimals
    if num == int(num):
        return int(num)
    else:
        return num

def reason(rT, msg) :
  #rT.reason = (rT.reason ? rT.reason + '. ' : '') + msg;
  if rT['reason'] :
    rT['reason'] += '. ' + msg
  else:
    rT['reason']  = '' + msg
  console_error(msg)

def getMaxSafeBasal(profile):       #tempBasalFunctions.getMaxSafeBasal = function getMaxSafeBasal(profile) {
    if 'max_daily_safety_multiplier' in profile:
        max_daily_safety_multiplier = profile['max_daily_safety_multiplier']
    else:
        max_daily_safety_multiplier = 3
    if 'current_basal_safety_multiplier' in profile:    
        current_basal_safety_multiplier = profile['current_basal_safety_multiplier']
    else:
        current_basal_safety_multiplier = 4

    return min(profile['max_basal'], max_daily_safety_multiplier * profile['max_daily_basal'], current_basal_safety_multiplier * profile['current_basal'])

def setTempBasal(rate, duration, profile, rT, currenttemp, Flows):
    #//var maxSafeBasal = Math.min(profile.max_basal, 3 * profile.max_daily_basal, 4 * profile.current_basal);

    maxSafeBasal = getMaxSafeBasal(profile)
    #var round_basal = require('./round-basal');

    if (rate < 0) :
        rate = 0
    elif (rate > maxSafeBasal) :
        rate = maxSafeBasal
    

    suggestedRate = round_basal(rate, profile)
    if (typeof(currenttemp) != 'undefined' and typeof(currenttemp, 'duration') != 'undefined' and typeof(currenttemp,'rate') != 'undefined' and currenttemp['duration'] > (duration-10) and currenttemp['duration'] <= 120 and suggestedRate <= currenttemp['rate'] * 1.2 and suggestedRate >= currenttemp['rate'] * 0.8 and duration > 0 ) :
        rT['reason'] += " "+str(currenttemp['duration'])+"m left and " + str(currenttemp['rate']) + " ~ req " + str(suggestedRate) + "U/hr: no temp required"
        Flows.append(dict(title="new temp settings\nclose to current ones\nno change", indent='+0', adr='sTB_32'))
        Flows.append(dict(title="R E T U R N\nkeep rate="+str(currenttemp['rate'])+"\nduration="+str(currenttemp['duration']), indent='+0', adr='sTB_33'))
        return rT
    

    if (suggestedRate == profile['current_basal']) :
      if (profile['skip_neutral_temps'] == True) :
        Flows.append(dict(title="skip_neutral_temps\nis True", indent='+0', adr='sTB_37'))
        if (typeof(currenttemp) != 'undefined' and typeof(currenttemp,'duration') != 'undefined' and currenttemp['duration'] > 0) :
          reason(rT, 'Suggested rate is same as profile rate, a temp basal is active, canceling current temp')
          rT['duration'] = 0
          rT['rate'] = 0
          Flows.append(dict(title="new rate = profile\na temp basal is active\ncanceling current temp", indent='+1', adr='sTB_39'))
          Flows.append(dict(title="R E T U R N\nback to profile\nbasal="+str(profile['current_basal']), indent='+0', adr='sTB_42'))
          return rT
        else :
          reason(rT, 'Suggested rate is same as profile rate, no temp basal is active, doing nothing')
          Flows.append(dict(title="new rate = profile rate\nno temp basal is active\ndoing nothing", indent='+1', adr='sTB_48'))
          Flows.append(dict(title="R E T U R N\nkeep rate="+str(suggestedRate)+"\nduration="+str(currenttemp['duration']), indent='+0', adr='sTB_'))
          return rT
        
      else :
        reason(rT, 'Setting neutral temp basal of ' + str(profile['current_basal']) + 'U/hr')
        rT['duration'] = duration
        rT['rate'] = suggestedRate
        Flows.append(dict(title="R E T U R N\nset rate="+str(suggestedRate)+"\nduration="+str(duration), indent='+0', adr='sTB_51'))
        return rT
      
    else :
      rT['duration'] = duration
      rT['rate'] = suggestedRate
      Flows.append(dict(title="R E T U R N\nset rate="+str(suggestedRate)+"\nduration="+str(duration), indent='+0', adr='sTB_56'))
      return rT

def enable_smb(profile, microBolusAllowed, meal_data, target_bg, Flows) :
    #// disable SMB when a high temptarget is set
    if (not microBolusAllowed) :
        console_error("SMB disabled (!microBolusAllowed)")
        return False
    elif (not profile['allowSMB_with_high_temptarget'] and profile['temptargetSet'] and target_bg > 100) :
        console_error("SMB disabled due to high temptarget of",target_bg)
        return False
    elif (meal_data['bwFound'] == True and profile['A52_risk_enable'] == False) :
        console_error("SMB disabled due to Bolus Wizard activity in the last 6 hours.")
        return False
        
    #// enable SMB/UAM if always-on (unless previously disabled for high temptarget)
    if (profile['enableSMB_always'] == True) :
        if (meal_data['bwFound']) :
            console_error("Warning: SMB enabled within 6h of using Bolus Wizard: be sure to easy bolus 30s before using Bolus Wizard")
        else :
            console_error("SMB enabled due to enableSMB_always")
        return True

    #// enable SMB/UAM (if enabled in preferences) while we have COB
    if (profile['enableSMB_with_COB'] == True and meal_data['mealCOB']) :
        if (meal_data['bwCarbs']) :
            console_error("Warning: SMB enabled with Bolus Wizard carbs: be sure to easy bolus 30s before using Bolus Wizard")
        else :
            console_error("SMB enabled for COB of",meal_data['mealCOB'])
        return True

    #// enable SMB/UAM (if enabled in preferences) for a full 6 hours after any carb entry
    #// (6 hours is defined in carbWindow in lib/meal/total.js)
    if (profile['enableSMB_after_carbs'] == True and meal_data['carbs'] ) :
        if (meal_data['bwCarbs']) :
            console_error("Warning: SMB enabled with Bolus Wizard carbs: be sure to easy bolus 30s before using Bolus Wizard");
        else :
            console_error("SMB enabled for 6h after carb entry")
        return True

    #// enable SMB/UAM (if enabled in preferences) if a low temptarget is set
    if (profile['enableSMB_with_temptarget'] == True and (profile['temptargetSet'] and target_bg < 100)) :
        if (meal_data['bwFound']) :
            console_error("Warning: SMB enabled within 6h of using Bolus Wizard: be sure to easy bolus 30s before using Bolus Wizard")                                                    
        else :
            console_error("SMB enabled for temptarget of",convert_bg(target_bg, profile))
        return True

    console_error("SMB disabled (no enableSMB preferences active or no condition satisfied)")
    return False

def capInsulin(insulinReq, myTarget, myBg, insulinCap, capFactor, Flows):
    # if Bg is below Target (especially over night) then reduce insulinReq 
    # this is in case a short rise due to noisy ES signal releases too much insulin and we stay below target all the time
    # mod 4c: allow negative InsReq to get below profile base rate
    #if                 myBg<myTarget and myTarget<95 and insulinCap :
    if insulinReq>0 and myBg<myTarget and myTarget<95 and insulinCap :
        # do it even without tempTarget, but only below bg of 95                    #### lastets status 26.Jun.2020
        #insulinRed = insulinReq *               pow(myBg / myTarget, 4)            #### gz mod3:  initialy power 2
        insulinRed = insulinReq * max(0, ( 1 - ( 1 - myBg / myTarget) *capFactor )) #### gz mod4b: weaker near target, stronger further away
        #insulinRed  = insulinReq *        ( 1 - ( 1 - myBg / myTarget) *capFactor )  #### gz mod4c: weaker near target, stronger further away; allow negative
        console_error("gz reduce insulinReq from", insulinReq, " to", insulinRed)
        Flows.append(dict(title="cap insulinReq\nfrom "+str(insulinReq)+" to "+str(round(insulinRed,2)), indent='+0', adr='cap_162'))
        return round(insulinRed, 2)
    else:
        console_error("gz keep insulinReq at", insulinReq)
        Flows.append(dict(title="keep insulinReq("+str(insulinReq)+")", indent='+0', adr='cap_166'))
        return insulinReq

def interpolate(xdata, profile):    # //, polygon)
    #// V14: interpolate ISF behaviour based on polygons defining nonlinear functions defined by value pairs for ...
    #//  ...      <-----  delta  ------->  or  <---------------  glucose  ------------------->
    polyX = [  2,   7,  12,  16,  20,       50,   60,   80,   90, 100, 110, 150, 180, 200]    #// later, hand it over
    polyY = [0.0, 0.0, 0.4, 0.7, 0.7,     -0.5, -0.5, -0.3, -0.2, 0.0, 0.0, 0.5, 0.7, 0.7]    #// later, hand it over
    polymax = len(polyX)-1
    step = polyX[0]
    sVal = polyY[0]
    stepT= polyX[polymax]
    sValold = polyY[polymax]
    #//console.error("Wertebereich ist ("+step+"/"+sVal+") - ("+stepT+"/"+sValold+")");

    newVal = 1
    lowVal = 1
    topVal = 1
    lowX = 1
    topX = 1
    myX = 1
    lowLabl = step

    if (step > xdata) :
        #// extrapolate backwards
        stepT = polyX[1]
        sValold = polyY[1]
        lowVal = sVal
        topVal = sValold
        lowX = step
        topX = stepT
        myX = xdata
        newVal = lowVal + (topVal-lowVal)/(topX-lowX)*(myX-lowX)
    elif (stepT < xdata) :
        #// extrapolate forwards
        step   = polyX[polymax-1]
        sVal   = polyY[polymax-1]
        lowVal = sVal
        topVal = sValold
        lowX = step
        topX = stepT
        myX = xdata
        newVal = lowVal + (topVal-lowVal)/(topX-lowX)*(myX-lowX)
    else :
        #// interpolate
        for i in range(polymax+1) :
            step = polyX[i]
            sVal = polyY[i]
            if (step == xdata) :
                newVal = sVal
                break
            elif (step > xdata) :
                topVal = sVal
                lowX= lowLabl
                myX = xdata
                topX= step
                newVal = lowVal + (topVal-lowVal)/(topX-lowX)*(myX-lowX)
                break
            lowVal = sVal
            lowLabl= step
    if ( xdata>100 )  : newVal = newVal * profile['higher_ISFrange_weight']    #// higher BG range
    elif ( xdata>40 ) : newVal = newVal * profile['lower_ISFrange_weight']     #// lower BG range, but not delta range
    else :              newVal = newVal * profile['delta_ISFrange_weight']     #// delta range
    return newVal

def autoISF(sens, target_bg, profile, glucose_status, meal_data, currentTime, autosens_data, sensitivityRatio, new_parameter, Fcasts, Flows, emulAI_ratio): 
    #### gz mod 6: dynamic ISF based on dimensions of 5% band
    #Fcasts['origISF'] = profile['sens']                        # taken from original logfile
    #Fcasts['autoISF'] = sens                                   # as modified by autosense; taken from original logfile
    emulAI_ratio.append(10.0)                                   # in case nothing changed
    Fcasts['BZ_ISF'] = profile['sens'] 
    Fcasts['Delta_ISF'] = profile['sens']  
    Fcasts['acceISF'] = profile['sens']  
    Fcasts['emulISF'] = sens
    #if 'use_autoisf' in profile:                               # version including pp-stuff required
    if not profile['use_autoisf']:
        console_error("autoISF disabled in Preferences")
        return sens
    #new_parameter['autoISF_flat'] = profile['use_autoisf']     # make new menu method the master setting
    dura05 = short(glucose_status['dura05'])                    # minutes of staying within +/-5% range
    avg05  = glucose_status['avg05']
    maxISFReduction = profile['autoisf_max']                    # mod 7d
    sens_modified = False
    pp_ISF = 1                                                  # mod 14f
    delta_ISF = 1                                               # mod 14f
    acce_ISF = 1                                                # mod 14j
    bg_off = target_bg+10 - avg05                               # move from central BG=100 to target+10 as virtual BG'=100
    
    #// start of mod V14j: calculate acce_ISF from bg acceleration and adapt ISF accordingly
    bg_acce = glucose_status['bg_acceleration']
    if (glucose_status['parabola_fit_a2'] !=0 ): 
        minmax_delta = - glucose_status['parabola_fit_a1']/2/glucose_status['parabola_fit_a2'] * 5       #// back from 5min block  1 min
        minmax_value = round(glucose_status['parabola_fit_a0'] - minmax_delta*minmax_delta/25*glucose_status['parabola_fit_a2'], 1)
        minmax_delta = round(minmax_delta, 1)
        if (minmax_delta<0 and bg_acce<0) :
            console_error("Parabolic fit saw maximum of", short(minmax_value), "about", short(-minmax_delta), "minutes ago")
        elif (minmax_delta<0 and bg_acce>0) :
            console_error("Parabolic fit saw minimum of", short(minmax_value), "about", short(-minmax_delta), "minutes ago")
        elif (minmax_delta>0 and bg_acce<0) :
            console_error("Parabolic fit predicts maximum of", short(minmax_value), "in about", short(minmax_delta), "minutes")
        elif (minmax_delta>0 and bg_acce>0) :
            console_error("Parabolic fit predicts minimum of", short(minmax_value), "in about", short(minmax_delta), "minutes")
    fit_corr = glucose_status['parabola_fit_correlation']
    if ( fit_corr<0.9 ) :
        console_error("acce_ISF adaptation by-passed as correlation", round(fit_corr,3), "is too low")
    else :
        fit_share = 10*(fit_corr-0.9)                           #// 0 at correlation 0.9, 1 at 1.00
        cap_weight = 1                                          #// full contribution above target
        if ( glucose_status['glucose']<profile['target_bg'] and bg_acce>1 ) :
            cap_weight = 0.5                                    #// halve the effect below target
        acce_weight = 0
        if ( bg_acce < 0 ) :
            acce_weight = profile['bgBrake_ISF_weight']
        else :
            acce_weight = profile['bgAccel_ISF_weight']
        if 'acce_ISF' in new_parameter:
            acce_ISF = new_parameter['acce_ISF']
        else:
            acce_ISF = 1 + bg_acce * cap_weight * acce_weight * fit_share
        console_error("acce_ISF adaptation is", short(round(acce_ISF,2)))
        Fcasts['acceISF'] = profile['sens'] / acce_ISF
        if ( acce_ISF != 1 ) :
            sens_modified = True
    #// end of mod V14j code block

    if 'bg_ISF' in new_parameter:
        bg_ISF = new_parameter['bg_ISF']
    else:
        bg_ISF = 1 + interpolate(100-bg_off, profile)
    console_error("bg_ISF adaptation is", short(round(bg_ISF,2)))
    Fcasts['BZ_ISF'] = profile['sens']  / bg_ISF
    if ( bg_ISF<1 and acce_ISF>1 ) :                                                                        #// mod V14j
        bg_ISF = bg_ISF * acce_ISF                                                                          #// mod V14j: bg_ISF could become > 1 now
        console_error("bg_ISF adaptation lifted to", round(bg_ISF,2), "as bg accelerates already")          #// mod V14j
    if (bg_ISF<1) :
        liftISF = min(bg_ISF, acce_ISF)
        if ( liftISF < profile['autoisf_min'] ) :                                                           #// mod V14j
            console_error("final ISF factor", short(round(liftISF,2)), "limited by autoisf_min", profile['autoisf_min'])  #// mod V14j
            liftISF = profile['autoisf_min']                                                                #// mod V14j
        #elif ( liftISF > maxISFReduction ) :                                                               #// mod V14j: not possible here
        #    console.error("final ISF factor", short(round(liftISF,2)), "limited by autoisf_max", maxISFReduction)  #// mod V14j
        #    liftISF = maxISFReduction                                                                      #// mod V14j
        Fcasts['Delta_ISF'] = profile['sens']  
        Fcasts['emulISF'] = sens / liftISF
        return min(720, round(profile['sens'] / min(sensitivityRatio, liftISF), 1))                         #// mod V14j: observe ISF maximum of 720(?)
    elif ( bg_ISF > 1 ) :
        sens_modified = True

    bg_delta = glucose_status['delta']
    if (bg_off > 0) :
        console_error("delta_ISF adaptation by-passed as average glucose < "+str(target_bg)+"+10")
    elif (glucose_status['short_avgdelta']<0) :
        console_error("delta_ISF adaptation by-passed as no rise or too short lived")
    elif (profile['enableppisf_always'] or profile['postmeal_ISF_duration'] >= (currentTime - meal_data['lastCarbTime']) / 1000/3600) :
        if 'pp_ISF' in new_parameter:
            pp_ISF = new_parameter['pp_ISF']
        else:
            pp_ISF = 1 + max(0, bg_delta * profile['postmeal_ISF_weight'])
        console_error("pp_ISF adaptation is", short(round(pp_ISF,2)))
        if (pp_ISF != 1) :
            sens_modified = True
    else :
        if 'delta_ISF' in new_parameter:
            delta_ISF = new_parameter['delta_ISF']
        else:
            delta_ISF = interpolate(bg_delta, profile)
        #//  mod V14d: halve the effect below target_bg+30
        if ( bg_off > -20 ) :
            delta_ISF = 0.5 * delta_ISF
        delta_ISF = 1 + delta_ISF
        console_error("delta_ISF adaptation is", short(round(delta_ISF,2)))
        if (delta_ISF != 1) :
            sens_modified = True

    dura_ISF = 1
    weightISF = profile['autoisf_hourlychange']           #// mod 7d: specify factor directly; use factor 0 to shut autoISF OFF
    if (meal_data['mealCOB']>0 and not profile['enableautoisf_with_COB']) :
        console_error("dura_ISF by-passed; preferences disabled mealCOB of "+round(meal_data.mealCOB,1))    #// mod 7f
    elif (dura05<10) :
        console_error("dura_ISF by-passed; bg is only "+str(dura05)+"m at level", short(avg05))
    elif (avg05 <= target_bg) :
        console_error("dura_ISF by-passed; avg. glucose", avg05, "below target", target_bg)
    else :
        #// # fight the resistance at high levels
        dura05_weight = dura05 / 60
        avg05_weight = weightISF / target_bg;                                      #// mod gz7b: provide access from AAPS
        dura_ISF += dura05_weight*avg05_weight*(avg05-target_bg)
        sens_modified = True
        console_error("dura_ISF  adaptation is", short(round(dura_ISF,2)), "because ISF", short(round(sens,1)), "did not do it for", short(round(dura05,1)),"m")
        emulAI_ratio[-1] = min(dura_ISF, maxISFReduction)*10

    if ( sens_modified ) :
        Fcasts['BZ_ISF'] = profile['sens'] / bg_ISF
        Fcasts['Delta_ISF'] = profile['sens'] / max(delta_ISF, pp_ISF)
        Fcasts['acceISF'] = profile['sens']  / acce_ISF
        liftISF = max(dura_ISF, bg_ISF, delta_ISF, acce_ISF, pp_ISF)                                                #// corrected logic on 30.Jan.2022
        if acce_ISF<1 :
            console_error("strongest ISF factor", short(round(liftISF,2)), "weakened to", short(round(liftISF*acce_ISF,2)), "as bg decelerates already")  #// mod V14j: brakes on for otherwise stronger or stable ISF
            liftISF = liftISF * acce_ISF                                                                            # put the deceleration brakes on
        if ( liftISF < profile['autoisf_min'] ) :                                                                   #// mod V14j: below minimum?
            console_error("final ISF factor", short(round(liftISF,2)), "limited by autoisf_min", profile['autoisf_min'])   #// mod V14j
            liftISF = profile['autoisf_min']                                                                        #// mod V14j
        elif ( liftISF > maxISFReduction ) :                                                                        #// mod V14j
            console_error("final ISF factor", short(round(liftISF,2)), "limited by autoisf_max", maxISFReduction)          #// mod V14j
            liftISF = maxISFReduction                                                                               #// mod V14j
        if ( liftISF >= 1 ) :           final_ISF = max(liftISF, sensitivityRatio)
        if ( liftISF <  1 ) :           final_ISF = min(liftISF, sensitivityRatio)
        Fcasts['emulISF'] = profile['sens'] / final_ISF
        return round(profile['sens'] / final_ISF, 1)
    return sens
    
    ## insert flowchart things above

def determine_varSMBratio(profile, bg, target_bg, Flows):
    #// mod 12: let SMB delivery ratio increase from min to max depending on how much bg exceeds target
    if 'smb_delivery_ratio_bg_range' in profile:
        use_fixed_SMB_ratio = False
        if profile['smb_delivery_ratio_bg_range'] == 0 :
            use_fixed_SMB_ratio = True
    else:
        use_fixed_SMB_ratio = True
    if use_fixed_SMB_ratio:
        #// not yet upgraded to this version or deactivated in SMB extended menu
        console_error('SMB delivery ratio set to fixed value', profile['smb_delivery_ratio'])
        Flows.append(dict(title="SMB delivery ratio set\nto fixed value "+str(profile['smb_delivery_ratio']), indent='0', adr='varSMB_173+'))
        return profile['smb_delivery_ratio']
    lower_SMB = min(profile['smb_delivery_ratio_min'], profile['smb_delivery_ratio_max'])
    if (bg <= target_bg) :
        console_error('SMB delivery ratio limited by minimum value', lower_SMB)
        Flows.append(dict(title="SMB delivery ratio limited\nby minimum value "+str(lower_SMB), indent='0', adr='varSMB_178+'))
        return lower_SMB
    higher_SMB = max(profile['smb_delivery_ratio_min'], profile['smb_delivery_ratio_max'])
    higher_bg = target_bg + profile['smb_delivery_ratio_bg_range'];
    if (bg >= higher_bg) :
        console_error('SMB delivery ratio limited by maximum value', higher_SMB)
        Flows.append(dict(title="SMB delivery ratio limited\nby maximum value "+str(higher_SMB), indent='0', adr='varSMB_184+'))
        return higher_SMB
    new_SMB = lower_SMB + (higher_SMB - lower_SMB)*(bg-target_bg) / profile['smb_delivery_ratio_bg_range']
    console_error('SMB delivery ratio set to interpolated value', new_SMB)
    Flows.append(dict(title="SMB delivery ratio set\nto interpolated value "+str(round(new_SMB,3)), indent='0', adr='varSMB_188+'))
    return new_SMB

def determine_basal(glucose_status, currenttemp, iob_data, profile, autosens_data, meal_data, tempBasalFunctionsDummy, microBolusAllowed, reservoir_data, thisTime, Fcasts, Flows, emulAI_ratio):
    rT = {} #//short for requestedTemp

    deliverAt   = thisTime
    currentTime = thisTime
    
    Flows.append(dict(title='checking\ninput data sets', indent='0', adr='55'))
        
    #f (typeof (profile) == 'undefined' or typeof (profile.current_basal) == 'undefined'):
    if (                                   typeof(profile,'current_basal') == 'undefined') :
        rT['error'] ='Error: could not get current basal rate'
        return rT
    # unpack the new parameters                                     ###
    if 'new_parameter' in profile:
        new_parameter = profile['new_parameter']                    ###
        AAPS_Version = new_parameter['AAPS_Version']                ### required from 2.7 onwards
    
    profile_current_basal = round_basal(profile['current_basal'], profile)
    basal = profile_current_basal

    systemTime = thisTime       # int(round(time.time() * 1000)) was real time, not the historical time
    bgTime = glucose_status['date']
    minAgo = round( (systemTime - bgTime) / 60 / 1000 ,1)

    bg = glucose_status['glucose']
    if 'noise' in glucose_status:
        noise = glucose_status['noise']
    else :
        noise = 0                                                       # unspecified in versions < 2.7
    if AAPS_Version == '<2.7' :
        if (bg < 39) : #//Dexcom is in ??? mode or calibrating
            rT['reason'] = "CGM is calibrating or in ??? state"
        if (minAgo > 12 or minAgo < -5) :   #// Dexcom data is too old, or way in the future
            rT['reason'] = "If current system time "+str(systemTime)+" is correct, then BG data is too old. The last BG data was read "+str(minAgo)+"m ago at "+str(bgTime)
        if (bg < 39 or minAgo > 12 or minAgo < -5) :
            if (currenttemp['rate'] >= basal) : #// high temp is running
                rT['reason'] += ". Canceling high temp basal of "+str(currenttemp['rate'])
                rT['deliverAt'] = deliverAt
                rT['temp'] = 'absolute'
                rT['duration'] = 0
                rT['rate'] = 0
                Fcasts['emulISF'] = profile['sens']
                return rT
                #//return tempBasalFunctions.setTempBasal(basal, 30, profile, rT, currenttemp);
            elif ( currenttemp['rate'] == 0 and currenttemp['duration'] > 30 ) :    #//shorten long zero temps to 30m
                rT['reason'] += ". Shortening " + str(currenttemp['duration']) + "m long zero temp to 30m. "
                rT['deliverAt'] = deliverAt
                rT['temp'] = 'absolute'
                rT['duration'] = 30
                rT['rate'] = 0
                Fcasts['emulISF'] = profile['sens']
                return rT
                #//return tempBasalFunctions.setTempBasal(0, 30, profile, rT, currenttemp);
            else :  #//do nothing.
                rT['reason'] += ". Temp " + str(currenttemp['rate']) + " <= current basal " + str(basal) + "U/hr; doing nothing. "
                Fcasts['emulISF'] = profile['sens']
                return rT
    else:   # the new logic as of V2.7
        #// 38 is an xDrip error state that usually indicates sensor failure
        #// all other BG values between 11 and 37 mg/dL reflect non-error-code BG values, so we should zero temp for those
        if (bg <= 10 or bg == 38 or noise >= 3) :
            #//Dexcom is in ??? mode or calibrating, or xDrip reports high noise
            rT['reason'] = "CGM is calibrating, in ??? state, or noise is high"
        if (minAgo > 12 or minAgo < -5) :
            #// Dexcom data is too old, or way in the future
            rT['reason'] = "If current system time "+str(systemTime)+" is correct, then BG data is too old. The last BG data was read "+str(minAgo)+"m ago at "+str(bgTime)
            # if BG is too old/noisy, or is changing less than 1 mg/dL/5m for 45m, cancel any high temps and shorten any long zero temps
            # cherry pick from oref upstream dev cb8e94990301277fb1016c778b4e9efa55a6edbc
        if new_parameter['CheckLibreError'] :      #### GZ:    normally I deactivate this Libre specific test
            if (minAgo > 12 or minAgo < -5)  : 
                pass
            elif ( bg > 60 and glucose_status['delta'] == 0 and glucose_status['short_avgdelta'] > -1 and glucose_status['short_avgdelta'] < 1 and glucose_status['long_avgdelta'] > -1 and glucose_status['long_avgdelta'] < 1 ) :
                if 'last_cal' in glucose_status :
                    if glucose_status['last_cal'] < 3 :
                        rT['reason'] = "CGM was just calibrated"
                else :
                    rT['reason'] = "Error: CGM data is unchanged for the past ~45m"
            #// cherry pick from oref upstream dev cb8e94990301277fb1016c778b4e9efa55a6edbc
            if (bg <= 10 or bg == 38 or noise >= 3 or minAgo > 12 or minAgo < -5 or ( bg > 60 and glucose_status['delta'] == 0 and glucose_status['short_avgdelta'] > -1 and glucose_status['short_avgdelta'] < 1 and glucose_status['long_avgdelta'] > -1 and glucose_status['long_avgdelta'] < 1 )) :
                if (currenttemp['rate'] > basal) : # // high temp is running
                    rT['reason'] += ". Replacing high temp basal of "+str(currenttemp['rate'])+" with neutral temp of "+str(basal)
                    rT['deliverAt'] = deliverAt
                    rT['temp'] = 'absolute'
                    rT['duration'] = 30
                    rT['rate'] = basal
                    #//return tempBasalFunctions.setTempBasal(basal, 30, profile, rT, currenttemp);
                elif ( currenttemp['rate'] == 0 and currenttemp['duration'] > 30 ) : # //shorten long zero temps to 30m
                    rT['reason'] += ". Shortening " + str(currenttemp['duration']) + "m long zero temp to 30m. "
                    rT['deliverAt'] = deliverAt
                    rT['temp'] = 'absolute'
                    rT['duration'] = 30
                    rT['rate'] = 0
                    #//return tempBasalFunctions.setTempBasal(0, 30, profile, rT, currenttemp);
                else : # //do nothing.
                    rT['reason'] += ". Temp " + str(currenttemp['rate']) + " <= current basal " + str(basal) + "U/hr; doing nothing. "
                Fcasts['emulISF'] = profile['sens']
                return rT
    #console_error('Meal age is:', (currentTime - meal_data['lastCarbTime']) / 1000/3600, 'hours')

    max_iob = profile['max_iob']   #// maximum amount of non-bolus IOB OpenAPS will ever deliver

    #// if min and max are set, then set target to their average
    #min_bg = profile['min_bg']
    #max_bg = profile['max_bg']
    #target_bg = (min_bg + max_bg) / 2
    if (typeof (profile, 'min_bg') != 'undefined') :
            min_bg = profile['min_bg']
    if (typeof (profile, 'max_bg') != 'undefined') :
            max_bg = profile['max_bg']
    if (typeof (profile, 'min_bg') != 'undefined' and typeof (profile, 'max_bg') != 'undefined') :
        target_bg = (profile['min_bg'] + profile['max_bg']) / 2
    else :
        rT['error'] ='Error: could not determine target_bg. '
        return rT

    #sensitivityRatio;
    high_temptarget_raises_sensitivity = profile['exercise_mode'] or profile['high_temptarget_raises_sensitivity']
    normalTarget = 100          #// evaluate high/low temptarget against 100, not scheduled basal/target (which might change)
    if  'half_basal_exercise_target' in profile:
        halfBasalTarget = profile['half_basal_exercise_target']
    else:
        halfBasalTarget = 160   #// when temptarget is 160 mg/dL, run 50% basal (120 = 75%; 140 = 60%)
        #// 80 mg/dL with low_temptarget_lowers_sensitivity would give 1.5x basal, but is limited to autosens_max (1.2x by default)
    if AAPS_Version == '2.7' :
        HTToffset = 0
    else :
        HTToffset = 10
    Flows.append(dict(title="Impact of\ntemptarget("+str(target_bg)+")\non sensitivity ("+str(round(autosens_data['ratio'],2))+")", indent='0', adr='140'))
    if ( high_temptarget_raises_sensitivity and profile['temptargetSet'] and target_bg > normalTarget + HTToffset 
        or  profile['low_temptarget_lowers_sensitivity'] and profile['temptargetSet'] and target_bg < normalTarget ):
        #// w/ target 100, temp target 110 = .89, 120 = 0.8, 140 = 0.67, 160 = .57, and 200 = .44
        #// e.g.: Sensitivity ratio set to 0.8 based on temp target of 120; Adjusting basal from 1.65 to 1.35; ISF from 58.9 to 73.6
        #//sensitivityRatio = 2/(2+(target_bg-normalTarget)/40);
        c = halfBasalTarget - normalTarget
        sensitivityRatio = c/(c+target_bg-normalTarget)
        #// limit sensitivityRatio to profile.autosens_max (1.2x by default)
        sensitivityRatio = min(sensitivityRatio, profile['autosens_max'])
        sensitivityRatio = round(sensitivityRatio,2)
        console_error("Sensitivity ratio set to "+str(sensitivityRatio)+" based on temp target of "+str(target_bg)+"; ")
        Flows.append(dict(title="Sensitivity ratio set to "+str(sensitivityRatio)+"\nbased on temp target of "+str(target_bg), indent='1', adr='140-xx'))
    elif ( typeof(autosens_data) != 'undefined'  and autosens_data):
        sensitivityRatio = autosens_data['ratio']
        console_error("Autosens ratio: "+str(sensitivityRatio)+";")
        Flows.append(dict(title="Autosens ratio "+str(sensitivityRatio), indent='1', adr='140-x'))

    Flows.append(dict(title="Impact of\nautosense("+str(round(sensitivityRatio,3))+")\non  basal", indent='0', adr='140'))
    if (sensitivityRatio):
        basal = profile['current_basal'] * sensitivityRatio
        basal = round_basal(basal, profile)
        if (basal != profile_current_basal):
            console_error("Adjusting basal from",profile_current_basal, "to "+str(basal)+";")
            Flows.append(dict(title="Adjust basal("+str(profile_current_basal)+")\nto "+str(basal), indent='+1', adr='144'))
        else:
            console_error("Basal unchanged: "+str(basal)+ ";")
            Flows.append(dict(title="Basal ("+str(basal)+ ")\nunchanged", indent='+1', adr='146'))

    #// adjust min, max, and target BG for sensitivity, such that 50% increase in ISF raises target from 100 to 120
    Flows.append(dict(title='checking\ntemptargetSet', indent='0', adr='151'))
    if (profile['temptargetSet']):
        Flows.append(dict(title='True;\nnot adjusting\nwith autosens', indent='+1', adr='152'))
        #//console_error("Temp Target set, not adjusting with autosens; ")
        pass
    elif (typeof (autosens_data) != 'undefined' and autosens_data):
        Flows.append(dict(title='False; checking\nsensitivity_raises_target\nor\nresistance_lowers_target', indent='+1', adr='153'))
        if ( profile['sensitivity_raises_target'] and autosens_data['ratio'] < 1 or profile['resistance_lowers_target'] and autosens_data['ratio'] > 1 ):
            Flows.append(dict(title='True', indent='+1', adr='155'))
            #// with a target of 100, default 0.7-1.2 autosens min/max range would allow a 93-117 target range
            min_bg = round((min_bg - 60) / autosens_data['ratio']) + 60
            max_bg = round((max_bg - 60) / autosens_data['ratio']) + 60
            new_target_bg = round((target_bg - 60) / autosens_data['ratio']) + 60
            #// don't allow target_bg below 80
            new_target_bg = max(80, new_target_bg)
            Flows.append(dict(title="Checking:\ndon't allow\ntarget_bg < 80", indent='+0', adr='161'))
            if (target_bg == new_target_bg):
                Flows.append(dict(title='True; target_bg\nunchanged: '+str(new_target_bg) , indent='+1', adr='162'))
                console_error("target_bg unchanged: "+str(new_target_bg)+";")
            else:
                Flows.append(dict(title='False; target_bg\nfrom '+str(target_bg)+' to '+str(new_target_bg), indent='+1', adr='164'))
                console_error("target_bg from "+str(target_bg)+" to "+str(new_target_bg)+";")
            target_bg = new_target_bg

    if (typeof (iob_data) == 'undefined' ):
        rT['error']='Error: iob_data undefined. '
        return rT
    
    iobArray = iob_data['iobArray']    ############ why this ? ############################################################
    #if (len(iob_data) > 1): 
    #    iob_data = iobArray[0]
    #    #//console_error(JSON.stringify(iob_data[0]));
    
    if ('activity' not in iob_data or 'iob' not in iob_data ):
        rT['error'] ='Error: iob_data missing some property. '
        return rT

    #tick;
    if (glucose_status['delta'] > -0.5):
        tick = "+" + str(round(glucose_status['delta'],0))
    else:
        tick =       str(round(glucose_status['delta'],0))  # for python: make sure it is always string type

    #//minDelta = Math.min(glucose_status.delta, glucose_status.short_avgdelta, glucose_status.long_avgdelta);
    minDelta = min(glucose_status['delta'], glucose_status['short_avgdelta'])
    minAvgDelta = min(glucose_status['short_avgdelta'], glucose_status['long_avgdelta'])
    maxDelta = max(glucose_status['delta'], glucose_status['short_avgdelta'], glucose_status['long_avgdelta'])

    profile_sens = round(profile['sens'],1)
    sens = profile['sens']
    #Fcasts['origISF'] = sens
    if (typeof (autosens_data) != 'undefined' and autosens_data):
        sens = profile['sens'] / sensitivityRatio
        sens = round(sens, 1)
        Flows.append(dict(title="checking impact of\nautosens ratio("+str(sensitivityRatio)+")", indent='0', adr='203'))
        if (sens != profile_sens):
            Flows.append(dict(title="ISF from "+str(profile_sens)+"\nto "+str(sens), indent='+1', adr='204'))
            console_error("ISF from", profile_sens, "to", short(sens))
        else:
            Flows.append(dict(title="ISF unchanged("+str(short(sens))+")\nby autosense", indent='+1', adr='206'))
            console_error("ISF unchanged:",short(sens))
        #//console_error(" (autosens ratio "+sensitivityRatio+")");
    console_error("; CR:", profile['carb_ratio'])
    sens = autoISF(sens, target_bg, profile, glucose_status, meal_data, currentTime, autosens_data, sensitivityRatio, new_parameter, Fcasts, Flows, emulAI_ratio)
    
    #lastTempAge;
    if (typeof (iob_data['lastTemp']) != 'undefined' ):
        lastTempAge = round(( thisTime - iob_data['lastTemp']['date'] ) / 60000)  #// in minutes
        #// }  ---- added to not produce errors
    else:
        lastTempAge = 0

    #//console_error("currenttemp:",currenttemp,"lastTemp:",JSON.stringify(iob_data.lastTemp),"lastTempAge:",lastTempAge,"m");
    tempModulus = (lastTempAge + currenttemp['duration']) % 30
    console_error("currenttemp:"+str(currenttemp)+" lastTempAge: "+str(lastTempAge)+" m tempModulus: "+str(tempModulus)+" m")
    rT['temp'] = 'absolute'
    rT['deliverAt'] = deliverAt

    if AAPS_Version=='<2.7' :
        if ( microBolusAllowed and currenttemp and iob_data['lastTemp'] and currenttemp['rate'] != iob_data['lastTemp']['rate'] ):
            rT['reason'] = "Warning: currenttemp rate "+str(currenttemp['rate'])+" != lastTemp rate "+str(iob_data['lastTemp']['rate'] )+" from pumphistory; setting neutral temp of "+str(basal)+"."
            #eturn tempBasalFunctions.setTempBasal(basal, 30, profile, rT, currenttemp)
            Flows.append(dict(title="Warning:\ncurrenttemp rate["+str(currenttemp['rate'])+"]   \n   != lastTemp rate("+str(iob_data['lastTemp']['rate'] )+") from pump\nsetting neutral temp", indent='0', adr='227'))
            return                    setTempBasal(basal, 30, profile, rT, currenttemp, Flows)
    else:
        if ( microBolusAllowed and currenttemp and iob_data['lastTemp'] and currenttemp['rate'] != iob_data['lastTemp']['rate'] and lastTempAge>10 and currenttemp['duration'] ) :
            rT['reaso'] = "Warning: currenttemp rate "+str(currenttemp['rate'])+" != lastTemp rate "+str(iob_data['lastTemp']['rate'])+" from pumphistory; canceling temp"
            #eturn tempBasalFunctions.setTempBasal(0, 0, profile, rT, currenttemp);
            return                    setTempBasal(0, 0, profile, rT, currenttemp, Flows)
    
    Flows.append(dict(title="checking\ncurrenttemp and\niob_data['lastTemp'] and\ncurrenttemp['duration']>0", indent='0', adr='229'))
    if ( currenttemp and iob_data['lastTemp'] and currenttemp['duration'] > 0 ):
        #// TODO: fix this (lastTemp.duration is how long it has run; currenttemp.duration is time left
        #//if ( currenttemp.duration < iob_data.lastTemp.duration - 2) {
            #//rT.reason = "Warning: currenttemp duration "+currenttemp.duration+" << lastTemp duration "+round(iob_data.lastTemp.duration,1)+" from pumphistory; setting neutral temp of "+basal+".";
            #//return tempBasalFunctions.setTempBasal(basal, 30, profile, rT, currenttemp);
        #//}
        #//console_error(lastTempAge, round(iob_data.lastTemp.duration,1), round(lastTempAge - iob_data.lastTemp.duration,1));
        lastTempEnded = lastTempAge - iob_data['lastTemp']['duration']
        Flows.append(dict(title="True; checking\nlastTempEnded>5", indent='+1', adr='237'))
        if ( AAPS_Version=='<2.7' and lastTempEnded > 5 ):
            Flows.append(dict(title="True;  Warning:\ncurrenttemp running but\nlastTemp from pumphistory ended "+str(lastTempEnded)+"m ago\nsetting neutral temp of "+str(basal), indent='+1', adr='238'))
            rT['reason'] = "Warning: currenttemp running but lastTemp from pumphistory ended "+str(lastTempEnded)+"m ago; setting neutral temp of "+str(basal)+"."
            #//console_error(currenttemp, round(iob_data.lastTemp,1), round(lastTempAge,1));
            #eturn tempBasalFunctions.setTempBasal(basal, 30, profile, rT, currenttemp)
            return                    setTempBasal(basal, 30, profile, rT, currenttemp, Flows)
        elif ( AAPS_Version=='2.7' and lastTempEnded>5 and lastTempAge>10):
            Flows.append(dict(title="True;  Warning:\ncurrenttemp running but\nlastTemp from pumphistory ended "+str(lastTempEnded)+"m ago\ncancelling temp", indent='+1', adr='238'))
            rT['reason'] = "Warning: currenttemp running but lastTemp from pumphistory ended "+str(lastTempEnded)+"m ago; cancelling temp"
            #//console_error(currenttemp, round(iob_data.lastTemp,1), round(lastTempAge,1));
            #eturn tempBasalFunctions.setTempBasal(0, 30, profile, rT, currenttemp)
            return                    setTempBasal(0, 30, profile, rT, currenttemp, Flows)
        #// TODO: figure out a way to do this check that doesn't fail across basal schedule boundaries
        #//if ( tempModulus < 25 and tempModulus > 5 ) {
            #//rT.reason = "Warning: currenttemp duration "+currenttemp.duration+" + lastTempAge "+lastTempAge+" isn't a multiple of 30m; setting neutral temp of "+basal+".";
            #//console_error(rT.reason);
            #//return tempBasalFunctions.setTempBasal(basal, 30, profile, rT, currenttemp);
        #//}

    #//calculate BG impact: the amount BG "should" be rising or falling based on insulin activity alone
    bgi = round(( -iob_data['activity'] * sens * 5 ), 2)
    #// project deviations for 30 minutes
    deviation = round( 30 / 5 * ( minDelta - bgi ) )
    #// don't overreact to a big negative delta: use minAvgDelta if deviation is negative
    Flows.append(dict(title='checking\ndeviation<0', indent='0', adr='255'))
    if (deviation < 0):
        Flows.append(dict(title="True; checking\nminAvgDelta("+str(round(minAvgDelta,1))+") based\ndeviation<0", indent='+1', adr='256'))
        deviation = round( (30 / 5) * ( minAvgDelta - bgi ) )
        #// and if deviation is still negative, use long_avgdelta
        if (deviation < 0):
            Flows.append(dict(title="True; use\nlong_avgdelta("+str(round(glucose_status['long_avgdelta'],1))+")\nbased deviation", indent='+1', adr='259'))
            deviation = round( (30 / 5) * ( glucose_status['long_avgdelta'] - bgi ) )

    #// calculate the naive (bolus calculator math) eventual BG based on net IOB and sensitivity
    Flows.append(dict(title='checking\niob > 0', indent='0', adr='264'))
    if (iob_data['iob'] > 0):
        naive_eventualBG = round( bg - (iob_data['iob'] * sens) )
        Flows.append(dict(title="True\nnaive eventual BG("+str(naive_eventualBG)+")\nbased on sensitivity", indent='+1', adr='265'))
    else: #// if IOB is negative, be more conservative and use the lower of sens, profile.sens
        naive_eventualBG = round( bg - (iob_data['iob'] * min(sens, profile['sens']) ) )
        Flows.append(dict(title="False\nnaive eventual BG("+str(naive_eventualBG)+")\nbased on min(sens,profile['sens']", indent='+1', adr='267'))
    #// and adjust it for the deviation above
    eventualBG = naive_eventualBG + deviation
    #// calculate what portion of that is due to bolussnooze
    #//bolusContrib = iob_data.bolussnooze * sens;
    #// and add it back in to get snoozeBG, plus another 50% to avoid low-temping at mealtime
    #//naive_snoozeBG = round( naive_eventualBG + 1.5 * bolusContrib );
    #// adjust that for deviation like we did eventualBG
    #//snoozeBG = naive_snoozeBG + deviation;

    #// raise target for noisy / raw CGM data
    Flows.append(dict(title='checking for\nadv_target_adjustments\nand not temptargetSet', indent='0', adr='279'))
    if (AAPS_Version=='2.7' and noise >= 2) :
        #// increase target at least 10% (default 30%) for raw / noisy data
        # several of these profile properties are unknown for my Eversense which so far has noise=0 anyway
        noisyCGMTargetMultiplier = max( 1.1, profile.noisyCGMTargetMultiplier )
        #// don't allow maxRaw above 250
        maxRaw = min( 250, profile.maxRaw )
        adjustedMinBG = round(min(200, min_bg * noisyCGMTargetMultiplier ))
        adjustedTargetBG = round(min(200, target_bg * noisyCGMTargetMultiplier ))
        adjustedMaxBG = round(min(200, max_bg * noisyCGMTargetMultiplier ))
        console_error("Raising target_bg for noisy / raw CGM data, from "+target_bg+" to "+adjustedTargetBG+"; ")
        min_bg = adjustedMinBG
        target_bg = adjustedTargetBG
        max_bg = adjustedMaxBG
    #// adjust target BG range if needed to safely bring down high BG faster without causing lows
    elif ( bg > max_bg and profile['adv_target_adjustments'] and not profile['temptargetSet'] ):
        Flows.append(dict(title='True; calculate\nreduced targets', indent='+1', adr='280'))
        #// with target=100, as BG rises from 100 to 160, adjustedTarget drops from 100 to 80
        adjustedMinBG   = round(max(80, min_bg    - (bg - min_bg)   /3 ),0)
        adjustedTargetBG= round(max(80, target_bg - (bg - target_bg)/3 ),0)
        adjustedMaxBG   = round(max(80, max_bg    - (bg - max_bg)   /3 ),0)
        #// if eventualBG, naive_eventualBG, and target_bg aren't all above adjustedMinBG, don’t use it
        #//console_error("naive_eventualBG:",naive_eventualBG+", eventualBG:",eventualBG);
        Flows.append(dict(title='checking\nreduced MinBG\ntoo low', indent='+1',  adr='286'))
        if (eventualBG > adjustedMinBG and naive_eventualBG > adjustedMinBG and min_bg > adjustedMinBG) :
            console_error("Adjusting targets for high BG: min_bg from "+str(min_bg)+" to "+str(adjustedMinBG)+";")
            min_bg = adjustedMinBG
            Flows.append(dict(title="no\nreduced min_bg("+str(min_bg)+")", indent='+1',  adr='288'))
        else :
            Flows.append(dict(title="yes\nkeep min_bg("+str(min_bg)+")", indent='+1',  adr='290'))
            console_error("min_bg unchanged: "+str(min_bg)+";")
        #// if eventualBG, naive_eventualBG, and target_bg aren't all above adjustedTargetBG, don’t use it
        Flows.append(dict(title='checking\nreduced TargetBG\ntoo low', indent='-1',  adr='293'))
        if (eventualBG > adjustedTargetBG and naive_eventualBG > adjustedTargetBG and target_bg > adjustedTargetBG) :
            console_error("target_bg from "+str(target_bg)+" to "+str(adjustedTargetBG)+";")
            target_bg = adjustedTargetBG
            Flows.append(dict(title="no\nreduced target_bg("+str(target_bg)+")", indent='+1', adr='295'))
        else :
            Flows.append(dict(title="yes\nkeep target_bg("+str(target_bg)+")", indent='+1', adr='297'))
            console_error("target_bg unchanged: "+str(target_bg)+";")
        #// if eventualBG, naive_eventualBG, and max_bg aren't all above adjustedMaxBG, don’t use it
        Flows.append(dict(title='checking\nreduced maxBG\ntoo low', indent='-1', adr='300'))
        if (eventualBG > adjustedMaxBG and naive_eventualBG > adjustedMaxBG and max_bg > adjustedMaxBG) :
            Flows.append(dict(title="no\nreduce max_bg("+str(max_bg)+")", indent='+1', adr='301'))
            console_error("max_bg from "+str(max_bg)+" to "+str(adjustedMaxBG))
            max_bg = adjustedMaxBG
        else :
            Flows.append(dict(title="yes\nkeep max_bg("+str(max_bg)+")", indent='+1', adr='304'))
            console_error("max_bg unchanged: "+str(max_bg))

    expectedDelta = calculate_expected_delta(target_bg, eventualBG, bgi)
    #if (typeof (eventualBG) == 'undefined' or isNaN(eventualBG)) :
    if (                                  math.isnan(eventualBG)) :
        rT['error'] ='Error: could not calculate eventualBG. '
        return rT

    #// min_bg of 90 -> threshold of 65, 100 -> 70 110 -> 75, and 130 -> 85
    #### GZ mod 5: threshold is too low at low targets; see "...PID/Übergänge der AAPS Parameter.ods"
    threshold_ratio = new_parameter['thresholdRatio']                                       #### gz Mod 5 status 26.Jun.2020
    threshold = threshold_ratio * min_bg + 20                                               #### factor was 0.5
    if min_bg<=98 and threshold_ratio>0.5:  threshold = threshold + pow(98-min_bg, 2) / 98  #### reduce less and stay >=70
    threshold = round(threshold, 0)                                                         ####
    #//console_error(reservoir_data);

    rT = {
        'temp': 'absolute'
        , 'bg': bg
        , 'tick': tick
        , 'eventualBG': eventualBG
        , 'targetBG': target_bg
        , 'insulinReq': 0
        , 'reservoir' : reservoir_data          #// The expected reservoir volume at which to deliver the microbolus (the reservoir volume from right before the last pumphistory run)
        , 'deliverAt' : deliverAt               #// The time at which the microbolus should be delivered
        , 'sensitivityRatio' : sensitivityRatio #// autosens ratio (fraction of normal basal)
    }

    #// generate predicted future BGs based on IOB, COB, and current absorption rate

    #global COBpredBGs
    #global aCOBpredBGs
    #global IOBpredBGs
    #global UAMpredBGs
    #global ZTpredBGs
    COBpredBGs = []
    aCOBpredBGs = []
    IOBpredBGs = []
    UAMpredBGs = []
    ZTpredBGs = []
    COBpredBGs.append(bg)
    aCOBpredBGs.append(bg)
    IOBpredBGs.append(bg)
    ZTpredBGs.append(bg)
    UAMpredBGs.append(bg)

    #// enable SMB whenever we have COB or UAM is enabled
    #// SMB is disabled by default, unless explicitly enabled in preferences.json
    enableSMB=False
    #// disable SMB when a high temptarget is set
    Flows.append(dict(title='leave SMB off?', indent='0', adr='348'))
    if AAPS_Version=='2.7' :
        enableSMB = enable_smb(profile, microBolusAllowed, meal_data, target_bg, Flows)
    else:
        if (not microBolusAllowed) :
            Flows.append(dict(title='Yes; found\nSMB not allowed', indent='+1', adr='349'))
            console_error("SMB disabled (!microBolusAllowed)")
        elif (not profile['allowSMB_with_high_temptarget'] and profile['temptargetSet'] and target_bg > 100) :
            Flows.append(dict(title="Yes; SMB disabled\ndue to high temptarget of "+str(target_bg), indent='+1', adr='351'))
            console_error("SMB disabled due to high temptarget of "+str(target_bg))
            enableSMB=False
        #// enable SMB/UAM (if enabled in preferences) while we have COB
        elif (profile['enableSMB_with_COB'] == True and meal_data['mealCOB']) :
            Flows.append(dict(title="Check bwCarbs", indent='+1', adr='355'))
            if (meal_data['bwCarbs']) :
                Flows.append(dict(title="Check\nA52_risk_enable", indent='+1', adr='356'))
                if (profile['A52_risk_enable']) :
                    Flows.append(dict(title="Warning:\nSMB enabled with Bolus Wizard carbs:\nbe sure to easy bolus\n30s before using Bolus Wizard", indent='+1', adr='357'))
                    console_error("Warning: SMB enabled with Bolus Wizard carbs: be sure to easy bolus 30s before using Bolus Wizard")
                    enableSMB=True
                else :
                    Flows.append(dict(title="SMB not enabled\nfor Bolus Wizard COB", indent='+1', adr='360'))
                    console_error("SMB not enabled for Bolus Wizard COB")
            else :
                Flows.append(dict(title="SMB enabled for COB of "+str(round(meal_data['mealCOB'],2)), indent='+1', adr='363'))
                console_error("SMB enabled for COB of "+str(meal_data['mealCOB']))
                enableSMB=True
        #// enable SMB/UAM (if enabled in preferences) for a full 6 hours after any carb entry
        #// (6 hours is defined in carbWindow in lib/meal/total.js)
        elif (profile['enableSMB_after_carbs'] == True and meal_data['carbs'] ) :
            Flows.append(dict(title="Check bwCarbs", indent='+1', adr='369'))
            if (meal_data['bwCarbs']) :
                Flows.append(dict(title="Check\nA52_risk_enable", indent='+1', adr='370'))
                if (profile['A52_risk_enable']) :
                    Flows.append(dict(title="Warning:\nSMB enabled with Bolus Wizard carbs:\nbe sure to easy bolus\n30s before using Bolus Wizard", indent='+1', adr='371'))
                    console_error("Warning: SMB enabled with Bolus Wizard carbs: be sure to easy bolus 30s before using Bolus Wizard")
                    enableSMB=True
                else :
                    Flows.append(dict(title="SMB not enabled for Bolus Wizard carbs", indent='+1', adr='374'))
                    console_error("SMB not enabled for Bolus Wizard carbs")
            else :
                Flows.append(dict(title="SMB enabled for\n6h after carb entry", indent='+1', adr='377'))
                console_error("SMB enabled for 6h after carb entry")
                enableSMB=True
        #// enable SMB/UAM (if enabled in preferences) if a low temptarget is set
        elif (profile['enableSMB_with_temptarget'] == True and (profile['temptargetSet'] and target_bg < 100)) :
            Flows.append(dict(title="SMB/UAM set\nand target_bg<100", indent='+1', adr='382'))
            if (meal_data['bwFound']) :
                Flows.append(dict(title="Check\nA52_risk_enable", indent='+1', adr='383'))
                if (profile['A52_risk_enable']) :
                    Flows.append(dict(title="Warning:\nSMB enabled within\n6h of using Bolus Wizard:\nbe sure to easy bolus\n30s before using Bolus Wizard", indent='+1', adr='384'))
                    console_error("Warning: SMB enabled within 6h of using Bolus Wizard: be sure to easy bolus 30s before using Bolus Wizard")
                    enableSMB=True
                else :
                    Flows.append(dict(title="enableSMB_with_temptarget\nnot supported\nwithin 6h of using Bolus Wizard", indent='+1', adr='387'))
                    console_error("enableSMB_with_temptarget not supported within 6h of using Bolus Wizard")
            else :
                Flows.append(dict(title="SMB enabled\nfor temptarget of "+str(convert_bg(target_bg, profile)), indent='+1', adr='390'))
                console_error("SMB enabled for temptarget of "+str(convert_bg(target_bg, profile)))
                enableSMB=True
        #// enable SMB/UAM if always-on (unless previously disabled for high temptarget)
        elif (profile['enableSMB_always'] == True) :
            Flows.append(dict(title="enableSMB_always;\nchecking for bwFound("+str(meal_data['bwFound'])+")", indent='+1', adr='395'))
            if (meal_data['bwFound']) :
                Flows.append(dict(title="Check\nA52_risk_enable", indent='+1', adr='396'))
                if (profile['A52_risk_enable'] == True) :
                    Flows.append(dict(title="Warning:\nSMB enabled within\n6h of using Bolus Wizard:\nbe sure to easy bolus\n30s before using Bolus Wizard", indent='+1', adr='397'))
                    console_error("Warning: SMB enabled within 6h of using Bolus Wizard: be sure to easy bolus 30s before using Bolus Wizard")
                    enableSMB=True
                else :
                    Flows.append(dict(title="enableSMB_with_temptarget\nnot supported\nwithin 6h of using Bolus Wizard", indent='+1', adr='400'))
                    console_error("enableSMB_always not supported within 6h of using Bolus Wizard")
            else :
                Flows.append(dict(title="SMB enabled \ndue to\nenableSMB_always", indent='+1', adr='403'))
                console_error("SMB enabled due to enableSMB_always")
                enableSMB=True
        else :
            Flows.append(dict(title="SMB disabled\nno enableSMB\npreferences active", indent='+1', adr='407'))
            console_error("SMB disabled (no enableSMB preferences active)")
    #// enable UAM (if enabled in preferences)
    enableUAM=(profile['enableUAM'])

    #//console_error(meal_data);
    #// carb impact and duration are 0 unless changed below
    ci = 0
    cid = 0
    #// calculate current carb absorption rate, and how long to absorb all carbs
    #// CI = current carb impact on BG in mg/dL/5m
    ci = round((minDelta - bgi),1)
    uci = round((minDelta - bgi),1)
    #// ISF (mg/dL/U) / CR (g/U) = CSF (mg/dL/g)
    Flows.append(dict(title='checking\ntemptargetSet', indent='0', adr='422'))
    if (profile['temptargetSet'] and AAPS_Version=='<2.7') :
        #// if temptargetSet, use unadjusted profile.sens to allow activity mode sensitivityRatio to adjust CR
        Flows.append(dict(title='True; use unadjusted profile.sens\nto allow\nactivity mode sensitivityRatio\nto adjust CR', indent='+1', adr='424'))
        csf = profile['sens'] / profile['carb_ratio']
    else :
        #// otherwise, use autosens-adjusted sens to counteract autosens meal insulin dosing adjustments
        #// so that autotuned CR is still in effect even when basals and ISF are being adjusted by autosens
        Flows.append(dict(title='False; use autosens-adjusted sens\nto counteract \nmeal insulin dosing adjustments', indent='+1', adr='428'))
        csf = sens / profile['carb_ratio']
    console_error("profile.sens:",short(profile['sens']),"sens:",short(sens),"CSF:",csf);
    maxCarbAbsorptionRate = 30      #// g/h; maximum rate to assume carbs will absorb if no CI observed
    #// limit Carb Impact to maxCarbAbsorptionRate * csf in mg/dL per 5m
    maxCI = round(maxCarbAbsorptionRate*csf*5/60,1)
    if (ci > maxCI) :
        Flows.append(dict(title="Limiting carb impact\nfrom "+str(ci)+" to\n"+str(maxCI)+" mg/dL/5m ("+str(maxCarbAbsorptionRate)+"g/h)", indent='0', adr='434'))
        console_error("Limiting carb impact from "+str(short(ci))+" to "+str(maxCI)+" mg/dL/5m (", str(maxCarbAbsorptionRate), "g/h )")
        ci = maxCI

    #// set meal_carbimpact high enough to absorb all meal carbs over 6 hours
    #// total_impact (mg/dL) = CSF (mg/dL/g) * carbs (g)
    #//console_error(csf * meal_data.carbs);
    #// meal_carbimpact (mg/dL/5m) = CSF (mg/dL/g) * carbs (g) / 6 (h) * (1h/60m) * 5 (m/5m) * 2 (for linear decay)
    #//meal_carbimpact = round((csf * meal_data.carbs / 6 / 60 * 5 * 2),1)
    remainingCATimeMin = 3                  #// h; before carb absorption starts
    #// adjust remainingCATime (instead of CR) for autosens
    if sensitivityRatio :   remainingCATimeMin = remainingCATimeMin / sensitivityRatio
    #// 20 g/h means that anything <= 60g will get a remainingCATimeMin, 80g will get 4h, and 120g 6h
    #// when actual absorption ramps up it will take over from remainingCATime
    assumedCarbAbsorptionRate = 20          #// g/h; maximum rate to assume carbs will absorb if no CI observed
    remainingCATime = remainingCATimeMin    #// added by mike https://github.com/openaps/oref0/issues/884
    Flows.append(dict(title="Checking\nmeal_data['carbs']", indent='0', adr='449'))
    if (meal_data['carbs']) :
        #// if carbs * assumedCarbAbsorptionRate > remainingCATimeMin, raise it
        #// so <= 90g is assumed to take 3h, and 120g=4h
        Flows.append(dict(title="raise remainingCATimeMin\nso <= 90g take 3h\nand 120g=4h", indent='+1', adr='452'))
        remainingCATimeMin = max(remainingCATimeMin, meal_data['mealCOB']/assumedCarbAbsorptionRate)
        lastCarbAge = round(( thisTime - meal_data['lastCarbTime'] ) / 60000)
        #//console_error(meal_data.lastCarbTime, lastCarbAge);

        fractionCOBAbsorbed = ( meal_data['carbs'] - meal_data['mealCOB'] ) / meal_data['carbs']
        remainingCATime = remainingCATimeMin + 1.5 * lastCarbAge/60
        remainingCATime = round(remainingCATime,1)
        #//console_error(fractionCOBAbsorbed, remainingCATimeAdjustment, remainingCATime)
        console_error("Last carbs "+str(lastCarbAge)+" minutes ago; remainingCATime:", short(remainingCATime), "hours;", str(round(fractionCOBAbsorbed*100))+"% carbs absorbed")

    #// calculate the number of carbs absorbed over remainingCATime hours at current CI
    #// CI (mg/dL/5m) * (5m)/5 (m) * 60 (min/hr) * 4 (h) / 2 (linear decay factor) = total carb impact (mg/dL)
    totalCI = max(0, ci / 5 * 60 * remainingCATime / 2)
    #// totalCI (mg/dL) / CSF (mg/dL/g) = total carbs absorbed (g)
    totalCA = totalCI / csf
    remainingCarbsCap = 90          ;#// default to 90
    remainingCarbsFraction = 1
    if (profile['remainingCarbsCap']) :     remainingCarbsCap = min(90, profile['remainingCarbsCap'])
    if (profile['remainingCarbsFraction']): remainingCarbsFraction = min(1,profile['remainingCarbsFraction'])
    remainingCarbsIgnore = 1 - remainingCarbsFraction
    remainingCarbs = max(0, meal_data['mealCOB'] - totalCA - meal_data['carbs']*remainingCarbsIgnore)
    remainingCarbs = min(remainingCarbsCap,remainingCarbs)
    #// assume remainingCarbs will absorb in a /\ shaped bilinear curve
    #// peaking at remainingCATime / 2 and ending at remainingCATime hours
    #// area of the /\ triangle is the same as a remainingCIpeak-height rectangle out to remainingCATime/2
    #// remainingCIpeak (mg/dL/5m) = remainingCarbs (g) * CSF (mg/dL/g) * 5 (m/5m) * 1h/60m / (remainingCATime/2) (h)
    remainingCIpeak = remainingCarbs * csf * 5 / 60 / (remainingCATime/2)
    #//console_error(profile.min_5m_carbimpact,ci,totalCI,totalCA,remainingCarbs,remainingCI,remainingCATime);
    #//if (meal_data.mealCOB * 3 > meal_data.carbs) { }

    #// calculate peak deviation in last hour, and slope from that to current deviation
    slopeFromMaxDeviation = round(meal_data['slopeFromMaxDeviation'],2)
    #// calculate lowest deviation in last hour, and slope from that to current deviation
    slopeFromMinDeviation = round(meal_data['slopeFromMinDeviation'],2)
    #// assume deviations will drop back down at least at 1/3 the rate they ramped up
    slopeFromDeviations = min(slopeFromMaxDeviation,-slopeFromMinDeviation/3)
    #//console_error(slopeFromMaxDeviation);

    aci = 10
    #//5m data points = g * (1U/10g) * (40mg/dL/1U) / (mg/dL/5m)
    #// duration (in 5m data points) = COB (g) * CSF (mg/dL/g) / ci (mg/dL/5m)
    #// limit cid to remainingCATime hours: the reset goes to remainingCI
    if (ci == 0) :
        #// avoid divide by zero
        cid = 0
    else :
        cid = min(remainingCATime*60/5/2, max(0, meal_data['mealCOB'] * csf / ci ))
    acid = max(0, meal_data['mealCOB'] * csf / aci )
    #// duration (hours) = duration (5m) * 5 / 60 * 2 (to account for linear decay)
    console_error("Carb Impact:", short(ci), "mg/dL per 5m; CI Duration:", short(round(cid*5/60*2,1)), "hours; remaining CI (~2h peak):", short(round(remainingCIpeak,1)), "mg/dL per 5m")
    #//console_error("Accel. Carb Impact:",aci,"mg/dL per 5m; ACI Duration:",round(acid*5/60*2,1),"hours");
    minIOBPredBG = 999
    minCOBPredBG = 999
    minUAMPredBG = 999
    minGuardBG = bg
    minCOBGuardBG = 999
    minUAMGuardBG = 999
    minIOBGuardBG = 999
    minZTGuardBG = 999
    #minPredBG;
    #avgPredBG;
    IOBpredBG = eventualBG
    maxIOBPredBG = bg
    maxCOBPredBG = bg
    maxUAMPredBG = bg
    #//maxPredBG = bg;
    eventualPredBG = bg
    ##lastIOBpredBG
    lastCOBpredBG = -1          # inizialize if being unused
    #lastUAMpredBG
    lastUAMpredBG = -1          # inizialize if being unused
    UAMduration = 0
    remainingCItotal = 0
    remainingCIs = []
    predCIs = []
    #console_error('diag row 502 --> prerequisites')
    #console_error('ci=',ci,'cid=',cid,'csf=',csf,'aci=',aci,'acid=',acid,'uci=',uci, 'sens=',sens)
    #console_error("mealCOB=",meal_data['mealCOB'],'remainingCATime=',remainingCATime,'remainingCIpeak=',remainingCIpeak, 'SlopeFromDeviations=',slopeFromDeviations)
    Flows.append(dict(title="inner loop for 4 hour\ninitial predictions", indent='0', adr='529-603'))
    try :
        icount = 0                  # arrays were initialy populated with "bg"
        for iobTick in iobArray :
            icount += 1             #### position in iobArry; to flag where minima were found
            #//console_error(iobTick);
            predBGI = round(( -iobTick['activity'] * sens * 5 ), 2)
            predZTBGI = round(( -iobTick['iobWithZeroTemp']['activity'] * sens * 5 ), 2)
            #// for IOBpredBGs, predicted deviation impact drops linearly from current deviation down to zero
            #// over 60 minutes (data points every 5m)
            predDev = ci * ( 1 - min(1,len(IOBpredBGs)/(60/5)) )
            IOBpredBG = IOBpredBGs[-1] + predBGI + predDev
            #console_error('diag: row 514 --> IOBpredBGs = ' +str(IOBpredBGs))
            #// calculate predBGs with long zero temp without deviations
            ZTpredBG = ZTpredBGs[-1] + predZTBGI
            #// for COBpredBGs, predicted carb impact drops linearly from current carb impact down to zero
            #// eventually accounting for all carbs (if they can be absorbed over DIA)
            predCI = max(0, max(0,ci) * ( 1 - len(COBpredBGs)/max(cid*2,1) ) )
            predACI = max(0, max(0,aci) * ( 1 - len(COBpredBGs)/max(acid*2,1) ) )
            #// if any carbs aren't absorbed after remainingCATime hours, assume they'll absorb in a /\ shaped
            #// bilinear curve peaking at remainingCIpeak at remainingCATime/2 hours (remainingCATime/2*12 * 5m)
            #// and ending at remainingCATime h (remainingCATime*12 * 5m intervals)
            intervals = min( len(COBpredBGs), (remainingCATime*12)-len(COBpredBGs) )
            remainingCI = max(0, intervals / (remainingCATime/2*12) * remainingCIpeak )
            remainingCItotal += predCI+remainingCI
            remainingCIs.append(round(remainingCI)) #,0))
            predCIs.append(round(predCI))           #,0))
            #//console_error(round(predCI,1)+"+"+round(remainingCI,1)+" ");
            COBpredBG = COBpredBGs[-1] + predBGI + min(0,predDev) + predCI + remainingCI
            aCOBpredBG = aCOBpredBGs[-1] + predBGI + min(0,predDev) + predACI
            #// for UAMpredBGs, predicted carb impact drops at slopeFromDeviations
            #// calculate predicted CI from UAM based on slopeFromDeviations
            predUCIslope = max(0, uci + ( len(UAMpredBGs)*slopeFromDeviations ) )
            #// if slopeFromDeviations is too flat, predicted deviation impact drops linearly from
            #// current deviation down to zero over 3h (data points every 5m)
            predUCImax = max(0, uci * ( 1 - len(UAMpredBGs)/max(3*60/5,1) ) )
            #//console_error(predUCIslope, predUCImax);
            #// predicted CI from UAM is the lesser of CI based on deviationSlope or DIA
            predUCI = min(predUCIslope, predUCImax)
            if(predUCI>0) :
                #//console_error(UAMpredBGs.length,slopeFromDeviations, predUCI);
                UAMduration=round((len(UAMpredBGs)+1)*5/60,1)
            UAMpredBG = UAMpredBGs[-1] + predBGI + min(0, predDev) + predUCI
            #//console_error(predBGI, predCI, predUCI);
            #// truncate all BG predictions at 4 hours
            if ( len(IOBpredBGs)  < 48) : IOBpredBGs.append(IOBpredBG)
            if ( len(COBpredBGs)  < 48) : COBpredBGs.append(COBpredBG)
            if ( len(aCOBpredBGs) < 48) : aCOBpredBGs.append(aCOBpredBG)
            if ( len(UAMpredBGs)  < 48) : UAMpredBGs.append(UAMpredBG)
            if ( len(ZTpredBGs)   < 48) : ZTpredBGs.append(ZTpredBG)
            #// calculate minGuardBGs without a wait from COB, UAM, IOB predBGs
            if ( COBpredBG < minCOBGuardBG ) : 
                minCOBGuardBG = round(COBpredBG)
                minCOBGuardPos = icount
            if ( UAMpredBG < minUAMGuardBG ) : 
                minUAMGuardBG = round(UAMpredBG)
                minUAMGuardPos = icount
            if ( IOBpredBG < minIOBGuardBG ) : 
                minIOBGuardBG  = round(IOBpredBG)
                minIOBGuardPos = icount
            if ( ZTpredBG < minZTGuardBG ) : 
                minZTGuardBG = round(ZTpredBG)
                minZTGuardPos = icount
            #console_error('diag: row 552 --> round(ZTpredBG)=', round(ZTpredBG), 'minZTGuardBG:', minZTGuardBG)

            #// set minPredBGs starting when currently-dosed insulin activity will peak
            #// look ahead 60m (regardless of insulin type) so as to be less aggressive on slower insulins
            insulinPeakTime = 60
            #// add 30m to allow for insluin delivery (SMBs or temps)
            insulinPeakTime = 90
            insulinPeak5m = (insulinPeakTime/60)*12
            #//console_error(insulinPeakTime, insulinPeak5m, profile.insulinPeakTime, profile.curve);

            #// wait 90m before setting minIOBPredBG
            if ( len(IOBpredBGs) > insulinPeak5m and (IOBpredBG < minIOBPredBG) ) : minIOBPredBG = round(IOBpredBG)
            if                                      ( IOBpredBG > maxIOBPredBG )  : maxIOBPredBG = IOBpredBG
            #// wait 85-105m before setting COB and 60m for UAM minPredBGs
            if ( (cid or remainingCIpeak > 0) and len(COBpredBGs) > insulinPeak5m and (COBpredBG < minCOBPredBG) ) : minCOBPredBG = round(COBpredBG)
            if ( (cid or remainingCIpeak > 0) and COBpredBG > maxIOBPredBG ) : maxCOBPredBG = COBpredBG
            if ( enableUAM and len(UAMpredBGs) > 12 and (UAMpredBG < minUAMPredBG) ) : minUAMPredBG = round(UAMpredBG)
            if ( enableUAM and UAMpredBG > maxIOBPredBG ) : maxUAMPredBG = UAMpredBG
            
            #console_error('diag: interims predBGI=', predBGI, 'predZTBGI=', predZTBGI, 'predDev=', predDev, 'predCI=', predCI, 'remainingCI=', remainingCI)
            #console_error('diag: end of loop --> IOBpredBG=', IOBpredBG, 'COBpredBG=', COBpredBG,'aCOBpredBG=', aCOBpredBG, 'UAMpredBG=', UAMpredBG, 'ZTpredBG=', ZTpredBG)
            #console_error('diag: end of loop --> minIOBPredBG=', minIOBPredBG,'maxIOBPredBG=', maxIOBPredBG)
            #console_error('diag: end of loop --> minCOBPredBG=', minCOBPredBG,'maxCOBPredBG=', maxCOBPredBG)
            #console_error('diag: end of loop --> minUAMPredBG=', minUAMPredBG,'maxUAMPredBG=', maxUAMPredBG)
            #console_error('diag: end of loop --> minCOBGuardBG=', minCOBGuardBG,'minUAMGuardBG=', minUAMGuardBG)
            #console_error('diag: end of loop --> minIOBGuardBG=', minIOBGuardBG,'minZTGuardBG=', minZTGuardBG)
        #// set eventualBG to include effect of carbs
        #//console_error("PredBGs:",JSON.stringify(predBGs));
        
        
    except: # catch *all* exceptions
        e = sys.exc_info()[0]
        console_error("Problem with iobArray.  Optional feature Advanced Meal Assist disabled:"+str(e))

    #### all initial predictions done and finalised
    Fcasts['COBinitBGs'] = copy.deepcopy(COBpredBGs)
    #casts['aCOBinitBGs'] = copy.deepcopy(aCOBpredBGs)
    Fcasts['IOBinitBGs'] = copy.deepcopy(IOBpredBGs)
    Fcasts['UAMinitBGs'] = copy.deepcopy(UAMpredBGs)
    Fcasts['ZTinitBGs']  = copy.deepcopy(ZTpredBGs)
    if (meal_data['mealCOB']) :
        #print('CIs', str(predCIs),'\nremainingCIs', str(remainingCIs))
        console_error("predCIs (mg/dL/5m):"+joinCIs(predCIs))
        console_error("remainingCIs:      "+joinCIs(remainingCIs))
    #//,"totalCA:",round(totalCA,2),"remainingCItotal/csf+totalCA:",round(remainingCItotal/csf+totalCA,2));
    rT['predBGs'] = {}
    Flows.append(dict(title="limit initial pred\nto range 39-401\ntruncate constant tails", indent='+1', adr='610-671'))
    for i in range(len(IOBpredBGs)) :
        IOBpredBGs[i] = round(min(401,max(39,IOBpredBGs[i])))
    for i in reversed(range(13, len(IOBpredBGs))) :
        if (IOBpredBGs[i-1] != IOBpredBGs[i]) : break
        else : IOBpredBGs.pop()
    
    rT['predBGs']['IOB'] = IOBpredBGs
    lastIOBpredBG=round(IOBpredBGs[len(IOBpredBGs)-1])
    for  i,p in enumerate(ZTpredBGs) :
        ZTpredBGs[i] = round(min(401,max(39,p)))
    for i in reversed(range(7, len(ZTpredBGs))) :
        #//if (ZTpredBGs[i-1] != ZTpredBGs[i]) { break; }
        #// stop displaying ZTpredBGs once they're rising and above target
        if (ZTpredBGs[i-1] >= ZTpredBGs[i] or ZTpredBGs[i] < target_bg) : break
        else : ZTpredBGs.pop()
    rT['predBGs']['ZT'] = ZTpredBGs
    lastZTpredBG=round(ZTpredBGs[len(ZTpredBGs)-1])
    if (meal_data['mealCOB'] > 0) :
        for  i,p in enumerate(aCOBpredBGs) :
            aCOBpredBGs[i] = round(min(401,max(39,p)))
        for i in reversed(range(13, len(aCOBpredBGs))) :
            if (aCOBpredBGs[i-1] != aCOBpredBGs[i]) : break
            else : aCOBpredBGs.pop()
        #// disable for now.  may want to add a preference to re-enable
        #//rT.predBGs.aCOB = aCOBpredBGs;
    if (meal_data['mealCOB'] > 0 and ( ci > 0 or remainingCIpeak > 0 )) :
        for  i,p in enumerate(COBpredBGs) :
            COBpredBGs[i] = round(min(401,max(39,p)));
        for i in reversed(range(13, len(COBpredBGs))) :
            if (COBpredBGs[i-1] != COBpredBGs[i]) : break
            else : COBpredBGs.pop()
        rT['predBGs']['COB'] = COBpredBGs
        lastCOBpredBG=round(COBpredBGs[len(COBpredBGs)-1])
        eventualBG = max(eventualBG, round(COBpredBGs[len(COBpredBGs)-1]) )

    if (ci > 0 or remainingCIpeak > 0) :
        if (enableUAM) :
            for  i,p in enumerate(UAMpredBGs) :
                UAMpredBGs[i] = round(min(401,max(39,p)))
            for i in reversed(range(13, len(UAMpredBGs))) :
                if (UAMpredBGs[i-1] != UAMpredBGs[i]) : break
                else : UAMpredBGs.pop()
            rT['predBGs']['UAM'] = UAMpredBGs
            lastUAMpredBG=round(UAMpredBGs[len(UAMpredBGs)-1])
            if (UAMpredBGs[len(UAMpredBGs)-1]) :
                eventualBG = max(eventualBG, round(UAMpredBGs[len(UAMpredBGs)-1]) )

        #// set eventualBG and snoozeBG based on COB or UAM predBGs
        rT['eventualBG'] = eventualBG
    
    console_error("UAM Impact:", short(uci), "mg/dL per 5m; UAM Duration:", short(UAMduration), "hours")

    minIOBPredBG = max(39,minIOBPredBG)
    minCOBPredBG = max(39,minCOBPredBG)
    minUAMPredBG = max(39,minUAMPredBG)
    minPredBG = round(minIOBPredBG)
    #console_error("diag: row 636 --> minPredBG:", minPredBG)

    if meal_data['carbs'] :         # extra line to avoid div!0 error
        fractionCarbsLeft = meal_data['mealCOB']/meal_data['carbs']
    #// if we have COB and UAM is enabled, average both
    Flows.append(dict(title="how to find\navgPredBG", indent='0', adr='683'))
    if ( minUAMPredBG < 999 and minCOBPredBG < 999 ) :
        #// weight COBpredBG vs. UAMpredBG based on how many carbs remain as COB
        avgPredBG = round( (1-fractionCarbsLeft)*UAMpredBG + fractionCarbsLeft*COBpredBG )
        Flows.append(dict(title=str(avgPredBG)+"; blend of\nUAMpredBG("+str(round(UAMpredBG))+")\nCOBpredBG("+str(round(COBpredBG))+")", indent='+1', adr='685'))
    #// if UAM is disabled, average IOB and COB
    elif ( minCOBPredBG < 999 ) :
        avgPredBG = round( (IOBpredBG + COBpredBG)/2 )
        Flows.append(dict(title=str(avgPredBG)+"; avg of\nIOBpredBG("+str(round(IOBpredBG))+")\nCOBpredBG("+str(round(COBpredBG))+")\nUAM disabled", indent='+1', adr='688'))
    #// if we have UAM but no COB, average IOB and UAM
    elif ( minUAMPredBG < 999 ) :
        avgPredBG = round( (IOBpredBG + UAMpredBG)/2 )
        Flows.append(dict(title=str(avgPredBG)+"; weighted avg of\nUAMpredBG("+str(round(UAMpredBG))+")\nIOBpredBG("+str(round(IOBpredBG))+")\nno COB", indent='+1', adr='691'))
    else :
        avgPredBG = round( IOBpredBG )
        Flows.append(dict(title=str(avgPredBG)+"; just from\nIOBpredBG", indent='+1', adr='693'))
    #// if avgPredBG is below minZTGuardBG, bring it up to that level
    if ( minZTGuardBG > avgPredBG ) :
        avgPredBG = minZTGuardBG
        Flows.append(dict(title=str(avgPredBG)+"; but not below\nminZTGuardBG("+str(minZTGuardBG)+")", indent='+1', adr='697'))

    #// if we have both minCOBGuardBG and minUAMGuardBG, blend according to fractionCarbsLeft
    Flows.append(dict(title="how to find\nminGuardBG", indent='0', adr='701'))
    minGuardSource2 = ''                            # flag singls source
    if ( (cid or remainingCIpeak > 0) ) :
        if ( enableUAM ) :
            minGuardBG = fractionCarbsLeft*minCOBGuardBG + (1-fractionCarbsLeft)*minUAMGuardBG
            Flows.append(dict(title=str(round(minGuardBG))+"; blend of\nminUAMGuardBG("+str(minUAMGuardBG)+")\nminCOBGuardBG("+str(minCOBGuardBG)+")", indent='+1', adr='703'))
            ### test case is in AndroidAPS._2019-11-13_00-00-00.6
            if fractionCarbsLeft>0.5 :              # CrabsLeft dominate UAMGuard
                minGuardSource = 'COB'
                minGuardPos = minCOBGuardPos
                minGuardBG1 = minCOBGuardBG         # the main contribution
                minGuardSource2 = 'UAM'
                minGuardPos2 = minUAMGuardPos
                minGuardBG2 = minUAMGuardBG
            else :                                  # otherwise
                minGuardSource = 'UAM'
                minGuardPos = minUAMGuardPos
                minGuardBG1 = minUAMGuardBG         # the main contribution
                minGuardSource2 = 'COB'
                minGuardPos2= minCOBGuardPos
                minGuardBG2 = minCOBGuardBG
        else :
            minGuardBG  = minCOBGuardBG             # the main and only contribution
            Flows.append(dict(title=str(round(minGuardBG))+"; just from\nCOBGuardBG\nUAM not enabled", indent='+1', adr='705'))
            minGuardBG1 = minCOBGuardBG             # the main and only contribution
            minGuardSource = 'COB'
            minGuardPos = minCOBGuardPos
    elif ( enableUAM ) :
        minGuardBG  = minUAMGuardBG                 # the main and only contribution
        Flows.append(dict(title=str(round(minGuardBG))+"; just from\nUAMGuardBG\nno COB", indent='+1', adr='708'))
        minGuardBG1 = minUAMGuardBG                 # the main and only contribution
        minGuardSource = 'COB'
        minGuardSource = 'UAM'
        minGuardPos = minUAMGuardPos
    else :
        minGuardBG  = minIOBGuardBG                 # the main and only contribution
        Flows.append(dict(title=str(round(minGuardBG))+"; just from\nIOBGuardBG\nno COB\nUAM not enabled", indent='+1', adr='710'))
        minGuardBG1 = minIOBGuardBG                 # the main and only contribution
        minGuardSource = 'COB'
        minGuardSource = 'IOB'
        minGuardPos = minIOBGuardPos
    minGuardBG = round(minGuardBG)
    #//console_error(minCOBGuardBG, minUAMGuardBG, minIOBGuardBG, minGuardBG);

    minZTUAMPredBG = minUAMPredBG
    Flows.append(dict(title="keep "+str(minZTUAMPredBG)+" as\nminZTUAMPredBG ?", indent='0', adr='718'))
    #// if minZTGuardBG is below threshold, bring down any super-high minUAMPredBG by averaging
    #// this helps prevent UAM from giving too much insulin in case absorption falls off suddenly
    if ( minZTGuardBG < threshold ) :
        minZTUAMPredBG = (minUAMPredBG + minZTGuardBG) / 2
        Flows.append(dict(title="use "+str(minZTUAMPredBG)+"\ndue to threshold of "+str(threshold), indent='+1', adr='719'))
    #// if minZTGuardBG is between threshold and target, blend in the averaging
    elif ( minZTGuardBG < target_bg ) :
        #// target 100, threshold 70, minZTGuardBG 85 gives 50%: (85-70) / (100-70)
        blendPct = (minZTGuardBG-threshold) / (target_bg-threshold)
        blendedMinZTGuardBG = minUAMPredBG*blendPct + minZTGuardBG*(1-blendPct)
        minZTUAMPredBG = (minUAMPredBG + blendedMinZTGuardBG) / 2
        Flows.append(dict(title=str(round(minZTUAMPredBG))+"; blended from\nminZTGuardBG("+str(minZTGuardBG)+")\nminUAMPredBG("+str(minUAMPredBG)+")\ndue to target of "+str(target_bg), indent='+1', adr='725'))
        #//minZTUAMPredBG = minUAMPredBG - target_bg + minZTGuardBG;
    #// if minUAMPredBG is below minZTGuardBG, bring minUAMPredBG up by averaging
    #// this allows more insulin if lastUAMPredBG is below target, but minZTGuardBG is still high
    elif ( minZTGuardBG > minUAMPredBG ) :
        minZTUAMPredBG = (minUAMPredBG + minZTGuardBG) / 2
        Flows.append(dict(title=str(minZTUAMPredBG)+"; avg of\nminZTGuardBG("+str(minZTGuardBG)+")\nminUAMPredBG("+str(minUAMPredBG)+")", indent='+1', adr='730'))
    minZTUAMPredBG = round(minZTUAMPredBG)
    #//console_error("minUAMPredBG:",minUAMPredBG,"minZTGuardBG:",minZTGuardBG,"minZTUAMPredBG:",minZTUAMPredBG);
    #// if any carbs have been entered recently
    if (meal_data['carbs']) :
        #// average the minIOBPredBG and minUAMPredBG if available
        """/*
        if ( minUAMPredBG < 999 ) {
            avgMinPredBG = round( (minIOBPredBG+minUAMPredBG)/2 );
        } else {
            avgMinPredBG = minIOBPredBG;
        }
        */"""

        Flows.append(dict(title="how to find\nminPredBG ?", indent='0', adr='746'))
        #// if UAM is disabled, use max of minIOBPredBG, minCOBPredBG
        if ( not enableUAM and minCOBPredBG < 999 ) :
            minPredBG = round(max(minIOBPredBG, minCOBPredBG))
            Flows.append(dict(title=str(minPredBG)+"; max of\nminIOBPredBG\nminCOBPredBG", indent='+1', adr='747'))
            #console_error("diag: row 700 --> minPredBG:", minPredBG)
        #// if we have COB, use minCOBPredBG, or blendedMinPredBG if it's higher
        elif ( minCOBPredBG < 999 ) :
            #// calculate blendedMinPredBG based on how many carbs remain as COB
            #//blendedMinPredBG = fractionCarbsLeft*minCOBPredBG + (1-fractionCarbsLeft)*minUAMPredBG;
            blendedMinPredBG = fractionCarbsLeft*minCOBPredBG + (1-fractionCarbsLeft)*minZTUAMPredBG
            #// if blendedMinPredBG > minCOBPredBG, use that instead
            minPredBG = round(max(minIOBPredBG, minCOBPredBG, blendedMinPredBG))
            Flows.append(dict(title=str(minPredBG)+"; blend of\nminIOBPredBG("+str(minIOBPredBG)+")\nminCOBPredBG("+str(minCOBPredBG)+")\nminZTUAMPredBG("+str(minZTUAMPredBG)+")", indent='+1', adr='754'))
            #console_error("diag: row 709 --> minPredBG:", minPredBG)
        #// if carbs have been entered, but have expired, use minUAMPredBG
        elif AAPS_Version=='<2.7' or enableUAM :
            #//minPredBG = minUAMPredBG;
            minPredBG = minZTUAMPredBG
            Flows.append(dict(title=str(minPredBG)+"; carbs expired\nuse minZTUAMPredBG", indent='+1', adr='758'))
            #console_error("diag: row 713 --> minPredBG:", minPredBG)
        else:
            minPredBG = minGuardBG                                          
            Flows.append(dict(title=str(minPredBG)+"; use minGuardBG", indent='+1', adr='758+'))
    #// in pure UAM mode, use the higher of minIOBPredBG,minUAMPredBG
    elif ( enableUAM ) :
        #//minPredBG = round(Math.max(minIOBPredBG,minUAMPredBG));
        minPredBG = round(max(minIOBPredBG,minZTUAMPredBG))
        Flows.append(dict(title=str(minPredBG)+"; pure UAM; max of\nminZTUAMPredBG\nminIOBPredBG", indent='+1', adr='763'))
        #console_error("diag: row 718 --> minPredBG:", minPredBG)

    #// make sure minPredBG isn't higher than avgPredBG
    minPredBG = min( minPredBG, avgPredBG )
    Flows.append(dict(title=str(minPredBG)+"; use min of\nminPredBG("+str(minPredBG)+")\navgPredBG("+str(avgPredBG)+")", indent='+1', adr='767'))

    Levels = {}
    console_error("minPredBG: "+str(minPredBG)+" minIOBPredBG: "+str(minIOBPredBG)+" minZTGuardBG: "+str(minZTGuardBG))
    Levels['eventualBG'] = eventualBG
    Levels['minPredBG'] = minPredBG
    Levels['minIOBPredBG'] = minIOBPredBG
    Levels['minZTGuardBG'] = minZTGuardBG
    if (minCOBPredBG < 999) :
        console_error("minCOBPredBG: "+str(minCOBPredBG))
        Levels['minCOBPredBG'] = minCOBPredBG
    if (minUAMPredBG < 999) :
        console_error("minUAMPredBG: "+str(minUAMPredBG))
        Levels['minUAMPredBG'] = minUAMPredBG
    console_error("avgPredBG:",avgPredBG,"COB:",meal_data['mealCOB'],"/",meal_data['carbs'])
    Levels['avgPredBG'] = avgPredBG
    #// But if the COB line falls off a cliff, don't trust UAM too much:
    #// use maxCOBPredBG if it's been set and lower than minPredBG
    if ( maxCOBPredBG > bg ) :
        minPredBG = min(minPredBG, maxCOBPredBG)
        Flows.append(dict(title=str(minPredBG)+"; min of\nminPredBG\nmaxCOBPredBG\nwhich is > bg("+str(bg)+")", indent='+1', adr='780'))

    rT['COB']=meal_data['mealCOB']
    rT['IOB']=iob_data['iob']           ##### check this !!   ################################################
    
    rT['reason']="COB: " + str(round(meal_data['mealCOB'],1)) + ", Dev: " + str(convert_bg(deviation, profile)) + ", BGI: " + str(convert_bg(bgi, profile)) + ", ISF: " + str(convert_bg(sens, profile)) + ", CR: " + str(round(profile['carb_ratio'], 2)) + ", Target: " + str(convert_bg(target_bg, profile)) + ", minPredBG " + str(convert_bg(minPredBG, profile)) + ", minGuardBG " + str(convert_bg(minGuardBG, profile)) + ", IOBpredBG " + str(convert_bg(lastIOBpredBG, profile))
    if (lastCOBpredBG > 0) :
        rT['reason'] += ", COBpredBG " + str(convert_bg(lastCOBpredBG, profile))
    if (lastUAMpredBG > 0) :
        rT['reason'] += ", UAMpredBG " + str(convert_bg(lastUAMpredBG, profile))
    rT['reason'] += "; "
    #//bgUndershoot = threshold - Math.min(minGuardBG, Math.max( naive_eventualBG, eventualBG ));
    #// use naive_eventualBG if above 40, but switch to minGuardBG if both eventualBGs hit floor of 39
    #//carbsReqBG = Math.max( naive_eventualBG, eventualBG );
    carbsReqBG = naive_eventualBG
    Flows.append(dict(title=str(carbsReqBG)+" as\ncarbsReqBG ?", indent='0', adr='796'))
    if ( carbsReqBG < 40 ) :
        carbsReqBG = min( minGuardBG, carbsReqBG )
        Flows.append(dict(title="was <40; now "+str(carbsReqBG)+" as min of\nminGuardB\ncarbsReqBG", indent='+1', adr='798'))
    bgUndershoot = threshold - carbsReqBG
    #// calculate how long until COB (or IOB) predBGs drop below min_bg
    minutesAboveMinBG = 240
    minutesAboveThreshold = 240
    Flows.append(dict(title="max values of 240 for\nminutesAboveMinBG ?\nminutesAboveThreshold ?", indent='0', adr='802-803'))
    if (meal_data['mealCOB'] > 0 and ( ci > 0 or remainingCIpeak > 0 )) :
        for  i,p in enumerate(COBpredBGs) :
            #//console_error(COBpredBGs[i], min_bg);
            if ( p < min_bg ) :
                minutesAboveMinBG = 5*i
                break
        for  i,p in enumerate(COBpredBGs) :
            #//console_error(COBpredBGs[i], threshold);
            if ( p < threshold ) :
                minutesAboveThreshold = 5*i
                break
        Flows.append(dict(title="now with COB\nminutesAboveMinBG="+str(minutesAboveMinBG)+"\nminutesAboveThreshold="+str(minutesAboveThreshold), indent='+1', adr='808; 815'))
    else :
        for  i,p in enumerate(IOBpredBGs) :
            #//console_error(IOBpredBGs[i], min_bg);
            if ( p < min_bg ) :
                minutesAboveMinBG = 5*i
                break
        for  i,p in enumerate(IOBpredBGs) :
           #//console_error(IOBpredBGs[i], threshold);
            if ( p < threshold ) :
                minutesAboveThreshold = 5*i
                break
        Flows.append(dict(title="now without COB\nminutesAboveMinBG="+str(minutesAboveMinBG)+"\nminutesAboveThreshold="+str(minutesAboveThreshold), indent='+1', adr='823; 830'))

    #### all predictions done and finalised
    Fcasts['COBpredBGs'] = COBpredBGs
    #casts['aCOBpredBGs'] = aCOBpredBGs
    Fcasts['IOBpredBGs'] = IOBpredBGs
    Fcasts['UAMpredBGs'] = UAMpredBGs
    Fcasts['ZTpredBGs'] = ZTpredBGs
    Levels['threshold'] = threshold
    Levels['maxDelta'] = new_parameter['maxDeltaRatio'] * bg
    
    Fcasts['Levels'] = Levels
                    
    if (enableSMB and minGuardBG < threshold) :
        console_error("minGuardBG "+str(convert_bg(minGuardBG, profile))+" projected below "+str(convert_bg(threshold, profile))+" - disabling SMB")
        #//rT.reason += "minGuardBG "+minGuardBG+"<"+threshold+": SMB disabled; ";
        enableSMB = False
        Flows.append(dict(title="disabled SMB because\nminGuardBG("+str(minGuardBG)+")   \n   < threshold("+str(threshold)+")", indent='0', adr='839'))
        Fcasts['Levels']['SMBoff'] = 'minGuard('+str(minGuardBG)+') <   \n   threshold('+str(threshold)+')'
        Fcasts['Levels']['type'] = 'threshold'
        Fcasts['Levels']['value'] = threshold
        Fcasts['Levels']['minGuardBG1'] = minGuardBG1
        Fcasts['Levels']['source'] = minGuardSource
        Fcasts['Levels']['timePos'] = minGuardPos
        if minGuardSource2 != '':                   # blend of COB and UAM
            Fcasts['Levels']['source2'] = minGuardSource2
            Fcasts['Levels']['timePos2'] = minGuardPos2
            Fcasts['Levels']['minGuardBG2']= minGuardBG2
            Fcasts['Levels']['minGuardBG'] = minGuardBG
        
    #f ( maxDelta > 0.20 * bg ) : # why is this critical? if we are rising that fast we need SMB !  ###########################################
    if ( maxDelta > new_parameter['maxDeltaRatio'] * bg ) :                                         ##### allow this change via new_ parameter
        console_error("maxDelta "+str(convert_bg(maxDelta, profile))+" > "+str(100*new_parameter['maxDeltaRatio'])+"% of BG "+str(convert_bg(bg, profile))+" - disabling SMB")      ####
        rT['reason'] += "maxDelta "+str(convert_bg(maxDelta, profile))+" > "+str(100*new_parameter['maxDeltaRatio'])+"% of BG "+str(convert_bg(bg, profile))+": SMB disabled;"      ####
        enableSMB = False
        Flows.append(dict(title="disabled SMB because\nmaxDelta > "+str(new_parameter['maxDeltaRatio'])+" * bg("+str(bg)+")", indent='0', adr='844+1'))
        Fcasts['Levels']['SMBoff'] = 'maxDelta('+str(maxDelta)+') >   \n   '+str(100*new_parameter['maxDeltaRatio'])+'% of bg('+str(bg)+')'
        Fcasts['Levels']['type'] = 'maxDelta'
        Fcasts['Levels']['value'] = ( 1 - new_parameter['maxDeltaRatio'] ) * bg
        Fcasts['Levels']['minGuardBG1'] = bg
        Fcasts['Levels']['source'] = 'bg'
        Fcasts['Levels']['timePos'] = 0

    console_error("BG projected to remain above", convert_bg(min_bg, profile), "for", minutesAboveMinBG, "minutes")
    if ( minutesAboveThreshold < 240 or minutesAboveMinBG < 60 ) :
        console_error("BG projected to remain above", convert_bg(threshold,profile), "for", minutesAboveThreshold, "minutes")
        Flows.append(dict(title="BG projected to remain\nabove "+str(convert_bg(threshold,profile))+" for "+str(minutesAboveThreshold)+" minutes", indent='+1', adr='930'))
    #// include at least minutesAboveThreshold worth of zero temps in calculating carbsReq
    #// always include at least 30m worth of zero temp (carbs to 80, low temp up to target)
    #//zeroTempDuration = Math.max(30,minutesAboveMinBG);
    zeroTempDuration = minutesAboveThreshold
    #// BG undershoot, minus effect of zero temps until hitting min_bg, converted to grams, minus COB
    zeroTempEffect = profile['current_basal']*sens*zeroTempDuration/60
    #// don't count the last 25% of COB against carbsReq
    COBforCarbsReq = max(0, meal_data['mealCOB'] - 0.25*meal_data['carbs'])
    carbsReq = (bgUndershoot - zeroTempEffect) / csf - COBforCarbsReq
    zeroTempEffect = round(zeroTempEffect)
    carbsReq = round(carbsReq)
    console_error("naive_eventualBG:", naive_eventualBG, "bgUndershoot:", short(bgUndershoot), "zeroTempDuration:", zeroTempDuration, "zeroTempEffect:", zeroTempEffect, "carbsReq:", carbsReq)
    Fcasts['Levels']['naive_eventualBG'] = naive_eventualBG
    if ( carbsReq >= profile['carbsReqThreshold'] and minutesAboveThreshold <= 45 ) :
        rT['carbsReq'] = carbsReq
        rT['carbsReqWithin'] = minutesAboveThreshold
        rT['reason'] += str(carbsReq) + " add'l carbs req w/in " + str(minutesAboveThreshold) + "m; "

       #// don't low glucose suspend if IOB is already super negative and BG is rising faster than predicted
    if (bg < threshold and iob_data['iob'] < -profile['current_basal']*20/60 and minDelta > 0 and minDelta > expectedDelta) :
        rT['reason'] += "IOB "+str(iob_data['iob'])+" < " + str(round(-profile['current_basal']*20/60,2))
        rT['reason'] += " and minDelta " + str(convert_bg(minDelta, profile)) + " > " + "expectedDelta " + str(convert_bg(expectedDelta, profile)) + "; "
    #// predictive low glucose suspend mode: BG is / is projected to be < threshold
    elif  ( bg < threshold or minGuardBG < threshold ) :
        rT['reason'] += "minGuardBG " + str(convert_bg(minGuardBG, profile)) + "<" + str(convert_bg(threshold, profile))
        bgUndershoot = target_bg - minGuardBG
        worstCaseInsulinReq = bgUndershoot / sens
        durationReq = round(60*worstCaseInsulinReq / profile['current_basal'])
        durationReq = round(durationReq/30)*30
        #// always set a 30-120m zero temp (oref0-pump-loop will let any longer SMB zero temp run)
        durationReq = min(120,max(30,durationReq))
        #eturn tempBasalFunctions.setTempBasal(0, durationReq, profile, rT, currenttemp)
        Flows.append(dict(title="bg("+str(bg)+") < threshold("+str(short(threshold))+")\nor\nminGuardBG("+str(minGuardBG)+")    \n    < threshold("+str(short(threshold))+")", indent='0', adr='873+1'))
        return                    setTempBasal(0, durationReq, profile, rT, currenttemp, Flows)

    #// if not in LGS mode, cancel temps before the top of the hour to reduce beeping/vibration
    #// console.error(profile.skip_neutral_temps, rT.deliverAt.getMinutes()); "deliverAt":160... Unix time
    if AAPS_Version == '2.7':
        #f ( profile['skip_neutral_temps'] and rT['deliverAt']['.getMinutes()'] >= 55 ) :
        minsDiff = ( rT['deliverAt'] / 60 / 1000 ) % 60
        if ( profile['skip_neutral_temps'] and minsDiff >= 55 ) :
            rT['reason'] += "; Canceling temp at " + str(minsDiff) + "m before the hour. "
            #eturn tempBasalFunctions.setTempBasal(0, 0, profile, rT, currenttemp);
            return                    setTempBasal(0, 0, profile, rT, currenttemp, Flows)

    if new_parameter['insulinCapBelowTarget'] and bg<target_bg and target_bg<95 and thisTime > 1602512247000:
        insReqOffset = round((1-bg/target_bg) * 5.0 * new_parameter['CapFactor'], 1)
        Flows.append(dict(title="Cap insulinReq = True\nvirtual target +"+str(insReqOffset), indent='0', adr='884-1'))
        console_error("mod12: Cap insulinReq = True; virtual target", insReqOffset);
    else:
        insReqOffset = 0        
    if (eventualBG < min_bg) :      #// if eventual BG is below target:
        Flows.append(dict(title="eventualBG("+str(eventualBG)+")\n< min_bg("+str(min_bg)+")", indent='0', adr='884+1'))
        rT['reason'] += "Eventual BG " + str(convert_bg(eventualBG, profile)) + " < " + str(convert_bg(min_bg, profile))
        #// if 5m or 30m avg BG is rising faster than expected delta
        if ( minDelta > expectedDelta and minDelta > 0 and not carbsReq ) :
            Flows.append(dict(title="minDelta("+str(minDelta)+")>expectedDelta("+str(expectedDelta)+")\nminDelta("+str(minDelta)+")>0\nand not carbsReq", indent='+1', adr='887+1'))
            #// if naive_eventualBG < 40, set a 30m zero temp (oref0-pump-loop will let any longer SMB zero temp run)
            if (naive_eventualBG < 40) :
                rT['reason'] += ", naive_eventualBG < 40. ";
                Flows.append(dict(title="naive_eventualBG("+str(naive_eventualBG)+")\n< 40", indent='+1', adr='889+1'))
                #eturn tempBasalFunctions.setTempBasal(0, 30, profile, rT, currenttemp)
                return                    setTempBasal(0, 30, profile, rT, currenttemp, Flows)
            if (glucose_status['delta'] > minDelta) :
                rT['reason'] += ", but Delta " + tick + " > expectedDelta " + str(convert_bg(expectedDelta, profile))
                Flows.append(dict(title="but Delta " + tick + " > expectedDelta " + str(convert_bg(expectedDelta, profile)), indent='+1', adr='891+1'))
            else :
                #rT['reason'] += ", but Min. Delta " + str(minDelta.toFixed(2)) + " > Exp. Delta " + str(convert_bg(expectedDelta, profile))
                rT['reason'] += ", but Min. Delta " + str(round(minDelta,2)) + " > Exp. Delta " + str(convert_bg(expectedDelta, profile))
                Flows.append(dict(title="but Min. Delta " + str(round(minDelta,2)) + " > Exp. Delta " + str(convert_bg(expectedDelta, profile)), indent='+1', adr='894+1'))
            if (currenttemp['duration'] > 15 and (round_basal(basal, profile) == round_basal(currenttemp['rate'], profile))) :
                rT['reason'] += ", temp " + str(currenttemp['rate']) + " ~ req " + str(basal) + "U/hr. "
                Flows.append(dict(title="temp " + str(currenttemp['rate']) + " ~ req " + str(basal) + "U/hr", indent='+1', adr='898+1'))
                Flows.append(dict(title="R E T U R N\nset rate="+str(currenttemp['rate'])+"\nduration>15", indent='+0', adr='899+1'))
                return rT
            else :
                rT['reason'] += "; setting current basal of " + str(basal) + " as temp. "
                #eturn tempBasalFunctions.setTempBasal(basal, 30, profile, rT, currenttemp)
                Flows.append(dict(title="naive_eventualBG("+str(naive_eventualBG)+")\n< 40", indent='+1', adr='901+1'))
                return                    setTempBasal(basal, 30, profile, rT, currenttemp, Flows)

        #// calculate 30m low-temp required to get projected BG up to target
        #// use snoozeBG to more gradually ramp in any counteraction of the user's boluses
        #// multiply by 2 to low-temp faster for increased hypo safety
        #//insulinReq = 2 * Math.min(0, (snoozeBG - target_bg) / sens);
        insulinReq = 2 * min(0, (eventualBG - target_bg - insReqOffset) / sens)
        insulinReq = round( insulinReq , 2)
        Flows.append(dict(title="insulinReq="+str(insulinReq)+"\nfrom pred>target", indent='+0', adr='911+1'))
        #// calculate naiveInsulinReq based on naive_eventualBG
        naiveInsulinReq = min(0, (naive_eventualBG - target_bg) / sens)
        naiveInsulinReq = round( naiveInsulinReq , 2)
        if (minDelta < 0 and minDelta > expectedDelta) :
            #// if we're barely falling, newinsulinReq should be barely negative
            #//rT.reason += ", Snooze BG " + convert_bg(snoozeBG, profile);
            newinsulinReq = round(( insulinReq * (minDelta / expectedDelta) ), 2)
            #//console_error("Increasing insulinReq from " + insulinReq + " to " + newinsulinReq);
            Flows.append(dict(title="minDelta("+str(minDelta)+") negative\nbut above expectedDelta("+str(expectedDelta)+")\nraise insulinReq "+str(insulinReq)+" to "+str(newinsulinReq), indent='+1', adr='918+1'))
            insulinReq = newinsulinReq
        #insulinReq = capInsulin(insulinReq, target_bg, bg, new_parameter['insulinCapBelowTarget'], new_parameter['CapFactor'], Flows)      #### GZ mod4b: reduce overnight lows
        #// rate required to deliver insulinReq less insulin over 30m:
        rate = basal + (2 * insulinReq)
        rate = round_basal(rate, profile)
        #// if required temp < existing temp basal
        insulinScheduled = currenttemp['duration'] * (currenttemp['rate'] - basal) / 60
        #// if current temp would deliver a lot (30% of basal) less than the required insulin,
        #// by both normal and naive calculations, then raise the rate
        minInsulinReq = min(insulinReq,naiveInsulinReq)
        if (insulinScheduled < minInsulinReq - basal*0.3) :
            #rT['reason'] += ", "+str(currenttemp['duration']) + "m@" + str((currenttemp['rate']).toFixed(2)) + " is a lot less than needed. ";
            rT['reason'] += ", "+str(currenttemp['duration']) + "m@" + str(round(currenttemp['rate'], 2)) + " is a lot less than needed. ";
            #eturn tempBasalFunctions.setTempBasal(rate, 30, profile, rT, currenttemp)
            Flows.append(dict(title="current temp is\na lot less than needed", indent='+1', adr='931+1'))
            return                    setTempBasal(rate, 30, profile, rT, currenttemp, Flows)
        if (typeof (currenttemp) != 'undefined' and (currenttemp['duration'] > 5 and rate >= currenttemp['rate'] * 0.8)) :
            rT['reason'] += ", temp " + str(currenttemp['rate']) + " ~< req " + str(rate) + "U/hr. "
            Flows.append(dict(title="current temp\nis close to need", indent='+1', adr='935+1'))
            Flows.append(dict(title="R E T U R N\nset rate="+str(currenttemp['rate'])+" ?\nduration="+str(currenttemp['duration'])+" ?", indent='+0', adr='936+1'))
            return rT
        else :
            #// calculate a long enough zero temp to eventually correct back up to target
            if ( rate <=0 ) :
                Flows.append(dict(title="long enough zero temp to\neventually get back up to target", indent='+1', adr='940+1'))
                bgUndershoot = target_bg - naive_eventualBG
                worstCaseInsulinReq = bgUndershoot / sens
                durationReq = round(60*worstCaseInsulinReq / profile['current_basal'])
                if (durationReq < 0) :
                    durationReq = 0
                #// don't set an SMB zero temp longer than 60 minutess
                else :
                    durationReq = round(durationReq/30)*30
                    durationReq = min(60,max(0,durationReq))
                #//console_error(durationReq);
                #//rT.reason += "insulinReq " + insulinReq + "; "
                if (durationReq > 0) :
                    rT['reason'] += ", setting " + str(durationReq) + "m zero temp. "
                    Flows.append(dict(title="setting " + str(durationReq) + "m\nzero temp.", indent='+1', adr='953+1'))
                     #eturn tempBasalFunctions.setTempBasal(rate, durationReq, profile, rT, currenttemp)
                    return                    setTempBasal(rate, durationReq, profile, rT, currenttemp, Flows)
            else :
                rT['reason'] += ", setting " + str(rate) + "U/hr. "
                Flows.append(dict(title="setting " + str(rate) + "U/hr", indent='+1', adr='957+1'))
            #eturn tempBasalFunctions.setTempBasal(rate, 30, profile, rT, currenttemp)
            return                    setTempBasal(rate, 30, profile, rT, currenttemp, Flows)

    #// if eventual BG is above min but BG is falling faster than expected Delta
    if (minDelta < expectedDelta) :
        Flows.append(dict(title="minDelta("+str(minDelta)+")   \n   < expectedDelta("+str(expectedDelta)+")\nwhat now?", indent='0', adr='965+1'))
        #// if in SMB mode, don't cancel SMB zero temp
        if (not (microBolusAllowed and enableSMB)) :
            Flows.append(dict(title="not in\nSMB mode", indent='+1', adr='967+1'))
            if (glucose_status['delta'] < minDelta) :
                rT['reason'] += "Eventual BG " + str(convert_bg(eventualBG, profile)) + " > " + str(convert_bg(min_bg, profile)) + " but Delta " + str(convert_bg(tick, profile)) + " < Exp. Delta " + str(convert_bg(expectedDelta, profile))
                Flows.append(dict(title="Eventual BG(" + str(convert_bg(eventualBG, profile)) + ")   \n   > min_bg(" + str(convert_bg(min_bg, profile)) + ")\nbut\nDelta(" + tick + ") < Exp. Delta[" + str(convert_bg(expectedDelta, profile))+')', indent='+1', adr='968+1'))
            else :
                rT['reason'] += "Eventual BG " + str(convert_bg(eventualBG, profile)) + " > " + str(convert_bg(min_bg, profile)) + " but Min. Delta " + str(round(minDelta,2) )+ " < Exp. Delta " + str(convert_bg(expectedDelta, profile))
                Flows.append(dict(title="Eventual BG(" + str(convert_bg(eventualBG, profile)) + ") > min_bg(" + str(convert_bg(min_bg, profile)) + ")\nbut\nMin. Delta(" + str(round(minDelta,2) )+ ") < Exp. Delta(" + str(convert_bg(expectedDelta, profile))+')', indent='+1', adr='970+1'))
            if (currenttemp['duration'] > 15 and (round_basal(basal, profile) == round_basal(currenttemp['rate'], profile))) :
                rT['reason'] += ", temp " + str(currenttemp['rate']) + " ~ req " + str(basal) + "U/hr. "
                Flows.append(dict(title="R E T U R N\currenttemp(" + str(currenttemp['rate']) + ")   \n   ~ req (" + str(basal) + ") U/hr.", indent='+0', adr='974+1'))
                return rT
            else :
                rT['reason'] += "; setting current basal of " + str(basal) + " as temp. "
                Flows.append(dict(title="setting current basal\nof " + str(basal) + " as temp", indent='+1', adr='976+1'))
                 #eturn tempBasalFunctions.setTempBasal(basal, 30, profile, rT, currenttemp)
                return                    setTempBasal(basal, 30, profile, rT, currenttemp, Flows)
    #// eventualBG or minPredBG is below max_bg
    if (min(eventualBG,minPredBG) < max_bg) :
        Flows.append(dict(title="eventualBG("+str(eventualBG)+")   \n   or minPredBG("+str(minPredBG)+")\nis below max_bg("+str(max_bg)+")", indent='0', adr='983+1'))
        #// if in SMB mode, don't cancel SMB zero temp
        if (not (microBolusAllowed and enableSMB )) :
            Flows.append(dict(title="not in SMB mode\neventualBG("+str(convert_bg(eventualBG, profile))+")-minPredBG("+str(convert_bg(minPredBG, profile))+")\nin range: no temp required", indent='+1', adr='985+1'))
            rT['reason'] += str(convert_bg(eventualBG, profile))+"-"+str(convert_bg(minPredBG, profile))+" in range: no temp required"
            if (currenttemp['duration'] > 15 and (round_basal(basal, profile) == round_basal(currenttemp['rate'], profile))) :
                rT['reason'] += ", temp " + str(currenttemp['rate']) + " ~ req " + str(basal) + "U/hr. "
                Flows.append(dict(title="R E T U R N\nset rate="+str(currenttemp['rate'])+"\durationn="+str(basal), indent='+0', adr='988+1'))
                return rT
            else :
                rT['reason'] += "; setting current basal of " + str(basal) + " as temp. "
                Flows.append(dict(title="setting current basal\nof " + str(basal) + " as temp", indent='+1', adr='990+1'))
                #eturn tempBasalFunctions.setTempBasal(basal, 30, profile, rT, currenttemp)
                return                    setTempBasal(basal, 30, profile, rT, currenttemp, Flows)

    #// eventual BG is at/above target
    #// if iob is over max, just cancel any temps
    #// if we're not here because of SMB, eventual BG is at/above target
    if (AAPS_Version=='<2.7' and not (microBolusAllowed and rT['COB'])) \
    or (AAPS_Version== '2.7' and eventualBG >= max_bg) :
        rT['reason'] += "Eventual BG " + str(convert_bg(eventualBG, profile)) + " >= " + str(convert_bg(max_bg, profile)) + ", "
        Flows.append(dict(title="Eventual BG " + str(convert_bg(eventualBG, profile)) + " >= " + str(convert_bg(max_bg, profile)), indent='0', adr='1000+1'))
    if (iob_data['iob'] > max_iob) :
        rT['reason'] += "IOB " + str(round(iob_data['iob'],2)) + " > max_iob " + str(max_iob)
        Flows.append(dict(title="IOB(" + str(round(iob_data['iob'],2)) + ") > max_iob(" + str(max_iob)+")", indent='0', adr='1003+1'))
        if (currenttemp['duration'] > 15 and (round_basal(basal, profile) == round_basal(currenttemp['rate'], profile))) :
            rT['reason'] += ", temp " + str(currenttemp['rate']) + " ~ req " + str(basal) + "U/hr. "
            Flows.append(dict(title="R E T U R N\nset rate="+str(currenttemp['rate'])+"\durationn="+str(basal), indent='+0', adr='1006+1'))
            return rT
        else :
            rT['reason'] += "; setting current basal of " + str(basal) + " as temp. "
            Flows.append(dict(title="setting current basal\nof " + str(basal) + " as temp", indent='+1', adr='1008+1'))
            #eturn tempBasalFunctions.setTempBasal(basal, 30, profile, rT, currenttemp)
            return                    setTempBasal(basal, 30, profile, rT, currenttemp, Flows)
    else :  #// otherwise, calculate 30m high-temp required to get projected BG down to target

        #// insulinReq is the additional insulin required to get minPredBG down to target_bg
        #//console_error(minPredBG,eventualBG);
        #//insulinReq = round( (Math.min(minPredBG,eventualBG) - target_bg) / sens, 2);
        insulinReq = round( (min(minPredBG,eventualBG) - target_bg - insReqOffset) / sens, 2)
        Flows.append(dict(title="IOB(" + str(round(iob_data['iob'],2)) + ") <= max_iob(" + str(max_iob)+")\ninsulinReq="+str(insulinReq), indent='0', adr='1016+1'))
        #// when dropping, but not as fast as expected, reduce insulinReq proportionally
        #// to the what fraction of expectedDelta we're dropping at
        #//if (minDelta < 0 and minDelta > expectedDelta) {
            #//newinsulinReq = round(( insulinReq * (1 - (minDelta / expectedDelta)) ), 2);
            #//console_error("Reducing insulinReq from " + insulinReq + " to " + newinsulinReq + " for minDelta " + minDelta + " vs. expectedDelta " + expectedDelta);
            #//insulinReq = newinsulinReq;
        #//}
        #// if that would put us over max_iob, then reduce accordingly
        if (insulinReq > max_iob-iob_data['iob']) :
            rT['reason'] += "max_iob " + str(max_iob) + ", "
            Flows.append(dict(title="max_iob(" + str(max_iob)+") violation\nreduce insulinReq("+str(insulinReq)+") to "+ str(round(max_iob-iob_data['iob'],2)), indent='+1', adr='1027+1'))
            insulinReq = max_iob-iob_data['iob']

        #// rate required to deliver insulinReq more insulin over 30m:
        if thisTime > 1602512247000 :                           # the date/time after which the bug was fixed when to cap Insulin
            #print('capInsulin timing fixed because\n', str(thisTime),'\n>1602512247000')
            #insulinReq = capInsulin(insulinReq, target_bg, bg, new_parameter['insulinCapBelowTarget'], new_parameter['CapFactor'], Flows)          #### GZ mod4b: reduce overnight insulin
            rate = basal + (2 * insulinReq)
            rate = round_basal(rate, profile)
        else:
            #print('capInsulin timing still wrong\n', str(thisTime),'\n>1602512247000')
            rate = basal + (2 * insulinReq)
            rate = round_basal(rate, profile)
            insulinReq = capInsulin(insulinReq, target_bg, bg, new_parameter['insulinCapBelowTarget'], new_parameter['CapFactor'], Flows)          #### GZ mod4b: reduce overnight insulin; leave it here to ba compatible with wrong position in 2.7 actual
        insulinReq = round(insulinReq,3)
        rT['insulinReq'] = insulinReq
        #//console_error(iob_data.lastBolusTime);
        #// minutes since last bolus
        lastBolusAge = round(( thisTime - iob_data['lastBolusTime'] ) / 60000,1)
        #//console_error(lastBolusAge);
        #//console_error(profile.temptargetSet, target_bg, rT.COB);
        #// only allow microboluses with COB or low temp targets, or within DIA hours of a bolus
        if (microBolusAllowed and enableSMB and bg > threshold) :
            Flows.append(dict(title="in SMB mode and\nbg(" + str(bg) + ") > threshold(" + str(threshold)+")", indent='+0', adr='1043+1'))
            #// never bolus more than maxSMBBasalMinutes worth of basal
            mealInsulinReq = round( meal_data['mealCOB'] / profile['carb_ratio'] ,3)
            if AAPS_Version == '<2.7' :                                                                           #### the logic w/o UAM
                if (typeof (profile, 'maxSMBBasalMinutes') == 'undefined' ) :
                    maxBolus = round( profile['current_basal'] * 30 / 60 ,1)
                    Flows.append(dict(title="maxSMBBasalMinutes\nundefined\nsetting maxBolus=" + str(maxBolus), indent='+1', adr='1045+1'))
                    console_error("profile.maxSMBBasalMinutes undefined: defaulting to 30m")
                    console_error("gz maximSMB: from undefined maximBasalMinutes")                                  #### incl. GZ mod1
                #// if IOB covers more than COB, limit maxBolus to 30m of basal
                elif  ( iob_data['iob'] > mealInsulinReq and iob_data['iob'] > 0 ) :
                    console_error("IOB",iob_data['iob'],"> COB "+str(meal_data['mealCOB'])+"; mealInsulinReq =",short(mealInsulinReq))
                    #uplift = new_parameter['maxBolusIOBRatio']                                                     #### incl. GZ mod1
                    if new_parameter['maxBolusIOBUsual'] :
                        uplift = new_parameter['maxBolusIOBRatio']                                                  #### incl. GZ mod1
                        maxBolus = round( uplift * profile['current_basal'] * 30 / 60 ,1)                           #### incl. GZ mod1
                        Flows.append(dict(title="IOB data found\nsetting maxBolus=" + str(maxBolus), indent='+1', adr='1050+6'))
                    else :
                        uplift = new_parameter['maxBolusTargetRatio']                                               #### incl. GZ mod1
                        maxBolus = round(uplift * profile['current_basal'] * profile['maxSMBBasalMinutes'] /60 ,1)  #### incl. GZ mod1: same as below
                        Flows.append(dict(title="IOB data found\ngz special found\nsetting maxBolus=" + str(maxBolus), indent='+1', adr='1050+6'))
                    console_error("gz maximSMB: from IOB > MealInsulinReq")                                         #### incl. GZ mod1
                else :
                    console_error("profile.maxSMBBasalMinutes:",profile['maxSMBBasalMinutes'],"profile.current_basal:",profile['current_basal'])
                    uplift = new_parameter['maxBolusTargetRatio']                                                   #### incl. GZ mod1
                    maxBolus = round(uplift * profile['current_basal'] * profile['maxSMBBasalMinutes'] / 60 ,1)     #### incl. GZ mod1
                    Flows.append(dict(title="from\nmaxSMBBasalMinutes("+str(profile['maxSMBBasalMinutes'])+")\nsetting maxBolus=" + str(maxBolus), indent='+1', adr='1053+10'))
                    console_error("gz maximSMB: from currentBasal & maximBasalMinutes")                             #### incl. GZ mod1
                bolus_increment = 0.1                                                                               #### was fix before 2.7
            else:                                                                                                 #### the new logic incl. UAM
                #// gz mod 10: make the irregular mutiplier a user input
                if 'smb_max_range_extension' in profile:
                    uplift = profile['smb_max_range_extension']
                    #if (uplift > 1) :
                    #    console_error("gz SMB max range extended from default by factor", str(uplift))
                    #    Flows.append(dict(title="gz SMB max range extended from default by factor "+str(uplift), indent='+0', adr='1131'))
                elif new_parameter['maxBolusIOBUsual'] :
                    #uplift = new_parameter['maxBolusIOBRatio']                                                     #### incl. GZ mod1
                    uplift = new_parameter['maxBolusIOBRatio']                                                      #### incl. GZ mod1
                else :
                    uplift = new_parameter['maxBolusTargetRatio']                                                   #### incl. GZ mod1
                if (typeof (profile, 'maxSMBBasalMinutes') == 'undefined' ) :
                    maxBolus = round(uplift * profile['current_basal'] * 30 / 60 ,1)
                    Flows.append(dict(title="maxSMBBasalMinutes\nundefined\nsetting maxBolus=" + str(maxBolus), indent='+1', adr='1045+1'))
                    console_error("profile.maxSMBBasalMinutes undefined: defaulting to 30m")
                    console_error("gz maximSMB: from undefined maxSMBBasalMinutes")                                 #### incl. GZ mod1
                #// if IOB covers more than COB, limit maxBolus to 30m of basal
                elif  ( iob_data['iob'] > mealInsulinReq and iob_data['iob'] > 0 ) :
                    console_error("IOB",iob_data['iob'],"> COB "+str(meal_data['mealCOB'])+"; mealInsulinReq =",short(mealInsulinReq))
                    Flows.append(dict(title="IOB("+str(iob_data['iob'])+") covers\nmore than COB("+str(short(mealInsulinReq))+")\nlimit maxBolus to 30m basal", indent='+1', adr='1048+1'))
                    if profile['maxUAMSMBBasalMinutes'] :
                        console_error("profile.maxUAMSMBBasalMinutes:",profile['maxUAMSMBBasalMinutes'],"profile.current_basal:",profile['current_basal'])
                        #// was: maxBolus = round( profile.current_basal  *  profile.maxUAMSMBBasalMinutes   / 60 ,1);
                        maxBolus = round(uplift * profile['current_basal'] * profile['maxUAMSMBBasalMinutes'] /60 ,1)  #### incl. GZ mod1: same as below
                        Flows.append(dict(title="maxUAMSMBBasalMinutes("+str(profile['maxUAMSMBBasalMinutes'])+")\nand current_basal("+str(profile['current_basal'])+")\ndefine maxBolus=" + str(maxBolus), indent='+1', adr='1050+6'))
                    else:   
                        console_error("profile.maxUAMSMBBasalMinutes undefined: defaulting to 30m");
                        #// minor mod on 18.Nov2019 by ga-zelle
                        #// test triple the maxSMB to offset the low basal rates
                        #// was: maxBolus = round( profile.current_basal    * 30 / 60 ,1);
                        maxBolus = round( uplift * profile['current_basal'] * 30 / 60 ,1)
                        Flows.append(dict(title="maxUAMSMBBasalMinutes\not given, use 30mins\nand current_basal\nto define maxBolus=" + str(maxBolus), indent='+1', adr='1052+6'))
                else :
                    console_error("profile.maxSMBBasalMinutes:",profile['maxSMBBasalMinutes'],"profile.current_basal:",profile['current_basal'])
                    uplift = new_parameter['maxBolusTargetRatio']                                                   #### incl. GZ mod1
                    maxBolus = round(uplift * profile['current_basal'] * profile['maxSMBBasalMinutes'] / 60 ,1)     #### incl. GZ mod1
                    Flows.append(dict(title="from\nmaxSMBBasalMinutes("+str(profile['maxSMBBasalMinutes'])+")\nsetting maxBolus=" + str(maxBolus), indent='+1', adr='1053+10'))
                    #console_error("gz maximSMB: from currentBasal & maxSMBmBasalMinutes")                          #### incl. GZ mod1
                #// bolus 1/2 the insulinReq, up to maxBolus, rounding down to nearest 0.1U
                # was: microBolus = int(min(insulinReq/2,maxBolus)*10)/10                                           #### more courageos - I have no 2nd rig
                bolus_increment = profile['bolus_increment']
            roundSMBTo = 1 / bolus_increment
            #was: microBolus = int(min(insulinReq * new_parameter['SMBRatio'], maxBolus)*10)/10                   #### incl. GZ mod2: master was 0.5
            #// gz md 10: make the share of InsulinReq a user input
            smb_ratio = determine_varSMBratio(profile, bg, target_bg, Flows)    # gz mod 12: linear function ...
            microBolus = min(insulinReq*smb_ratio, maxBolus)
            #  reduce SMB only if COB==0 (not yet in master js)    ... and IOB>0 ???
            #if new_parameter['LessSMBatModerateBG'] and bg<new_parameter['LessSMBbelow'] \
            #  and meal_data['mealCOB']==0:  # and iob_data['iob']>=0:  #### test limit of 95
            if new_parameter['LessSMBatModerateBG'] and bg<new_parameter['LessSMBbelow']:  # and iob_data['iob']>=0:  #### test limit of 95
                LessSMBratio = round(min(1, new_parameter['LessSMBFactor']*(1 - bg/new_parameter['LessSMBbelow'])), 2)
                microBolus = microBolus * (1-LessSMBratio)
                console_error("modX: SMB reduced by " + str(100*LessSMBratio) + "% because bg("+str(bg)+") is below "+str(new_parameter['LessSMBbelow']))
                Flows.append(dict(title="modX: microBolus reduced\nby " + str(100*LessSMBratio) + "% to "+str(round(microBolus,2))+"\nbecause bg("+str(bg)+") is below "+str(round(new_parameter['LessSMBbelow'],0)), indent='+0', adr='1053+x'))
            microBolus = int(microBolus*roundSMBTo+0.0001)/roundSMBTo                       ### round it up, e.g. from 0.29999 to 0.3
            #// calculate a long enough zero temp to eventually correct back up to target
            smbTarget = target_bg
            worstCaseInsulinReq = (smbTarget - (naive_eventualBG + minIOBPredBG)/2 ) / sens
            durationReq = round(60*worstCaseInsulinReq / profile['current_basal'])

            #// if insulinReq > 0 but not enough for a microBolus, don't set an SMB zero temp
            if (insulinReq > 0 and microBolus < bolus_increment) :
                Flows.append(dict(title="microBolus is\nbelow "+str(bolus_increment)+"U\ndon't set an SMB zero temp", indent='+0', adr='1064+12'))
                durationReq = 0
            
            smbLowTempReq = 0
            if (durationReq <= 0) :
                durationReq = 0
            #// don't set a temp longer than 120 minutes; or longer than 60 in AAPS V2.7
            elif  (durationReq >= 30) :
                durationReq = round(durationReq/30)*30
                if AAPS_Version == '2.7':
                    temp120 =  60
                else:
                    temp120 = 120
                durationReq = min(temp120,max(0,durationReq))
                Flows.append(dict(title="Don't set temp rate\nlonger than "+str(temp120)+" minutes", indent='+0', adr='1073+12'))
            else :
                #// if SMB durationReq is less than 30m, set a nonzero low temp
                smbLowTempReq = round( basal * durationReq/30 ,2)
                durationReq = 30
                Flows.append(dict(title="SMB durationReq("+str()+")\nis less than 30m\nset a nonzero low temp", indent='+0', adr='1077+12'))
            rT['reason'] += " insulinReq " + str(insulinReq)
            if (microBolus >= maxBolus) :
                rT['reason'] +=  "; maxBolus " + str(maxBolus)
                Flows.append(dict(title="SMB "+str(round(microBolus,1))+"\nlimited by maxBolus "+str(maxBolus), indent='0', adr='1080'))
            if (durationReq > 0) :
                rT['reason'] += "; setting " + str(durationReq) + "m low temp of " + str(smbLowTempReq) + "U/h"
                Flows.append(dict(title="setting " + str(durationReq) + "m\nlow temp of " + str(smbLowTempReq) + "U/h", indent='0', adr='1211'))
            rT['reason'] += ". "

            #//allow SMBs every 3 minutes by default
            SMBInterval = 3
            if 'SMBInterval' in profile :
                #// allow SMBIntervals between 1 and 10 minutes
                SMBInterval = min(10, max(1,profile['SMBInterval']))

            nextBolusMins = int(SMBInterval-lastBolusAge)                           # round(SMBInterval-lastBolusAge,1)
            nextBolusSeconds = round((SMBInterval - lastBolusAge) * 60, 0) % 60
            #//console_error(naive_eventualBG, insulinReq, worstCaseInsulinReq, durationReq);
            console_error("naive_eventualBG "+str(naive_eventualBG)+", "+str(durationReq)+"m "+str(smbLowTempReq)+"U/h temp needed; last bolus "+str(lastBolusAge)+"m ago; maxBolus:", maxBolus)
            if (lastBolusAge > SMBInterval) :
                if (microBolus > 0) :
                    rT['units'] = microBolus
                    rT['reason'] += "Microbolusing " + str(microBolus) + "U. "
                    Flows.append(dict(title="Microbolusing " + str(round(microBolus,1)) + "U", indent='1', adr='1095+12'))
            else :
                rT['reason'] += "Waiting " + str(nextBolusMins) + "m " + str(nextBolusSeconds) + "s to microbolus again. "
                Flows.append(dict(title="Waiting " + str(nextBolusMins) + ":"+str(nextBolusSeconds+100)[1:3]+"\nto microbolus again", indent='+0', adr='1098+12'))
            #//rT.reason += ". ";

            #// if no zero temp is required, don't return yet; allow later code to set a high temp
            if (durationReq > 0) :
                rT['rate'] = smbLowTempReq
                rT['duration'] = durationReq
                Flows.append(dict(title="R E T U R N\nset rate=" + str(smbLowTempReq) + "\nduration="+str(durationReq), indent='+0', adr='1106+12'))
                return rT
            
            #// if insulinReq is negative, snoozeBG > target_bg, and lastCOBpredBG > target_bg, set a neutral temp
            #//if (insulinReq < 0 and snoozeBG > target_bg and lastCOBpredBG > target_bg) {
                #//rT.reason += "; SMB bolus snooze: setting current basal of " + basal + " as temp. ";
                #//return tempBasalFunctions.setTempBasal(basal, 30, profile, rT, currenttemp);
            #//}
        maxSafeBasal = getMaxSafeBasal(profile)
        #axSafeBasal = tempBasalFunctions['max_safe_basal']                    ### fixed value

        if (rate > maxSafeBasal) :
            rT['reason'] += "adj. req. rate: "+str(round(rate,2))+" to maxSafeBasal: "+str(round(maxSafeBasal,2))+", "
            Flows.append(dict(title="adj. req. rate: "+str(rate)+"\nto maxSafeBasal: "+str(round(maxSafeBasal,2)), indent='+0', adr='1120+12'))
            rate = round_basal(maxSafeBasal, profile)
        
        insulinScheduled = currenttemp['duration'] * (currenttemp['rate'] - basal) / 60
        if (insulinScheduled >= insulinReq * 2) :   #// if current temp would deliver >2x more than the required insulin, lower the rate
            rT['reason'] += str(currenttemp['duration']) + "m@" + str(round(currenttemp['rate'],2)) + " > 2 * insulinReq. Setting temp basal of " + str(rate) + "U/hr. "
            Flows.append(dict(title="current temp("+str(round(currenttemp['rate'],2))+")\nwould deliver >2x\nthe required insulin\nlower the rate", indent='+0', adr='1125+12'))
            #eturn tempBasalFunctions.setTempBasal(rate, 30, profile, rT, currenttemp)
            return                    setTempBasal(rate, 30, profile, rT, currenttemp, Flows)

        if (typeof (currenttemp, 'duration') == 'undefined' or currenttemp['duration'] == 0) :    #// no temp is set
            rT['reason'] += "no temp, setting " + str(rate) + "U/hr. "
            Flows.append(dict(title="no temp was set", indent='+0', adr='1130+12'))
            #eturn tempBasalFunctions.setTempBasal(rate, 30, profile, rT, currenttemp)
            return                    setTempBasal(rate, 30, profile, rT, currenttemp, Flows)

        if (currenttemp['duration'] > 5 and (round_basal(rate, profile) <= round_basal(currenttemp['rate'], profile))) :    #// if required temp <~ existing temp basal
            rT['reason'] += "temp " + str(currenttemp['rate']) + " >~ req " + str(rate) + "U/hr. "
            Flows.append(dict(title="required temp("+str(rate)+")\n<~ existing temp("+str(round(currenttemp['rate'],3))+")", indent='+0', adr='1135+12'))
            Flows.append(dict(title="R E T U R N\nkeep rate="+str(round(currenttemp['rate'],2))+" ?\nduration="+str(currenttemp['duration'])+" ?", indent='+0', adr='1136+12'))
            return rT
        
        #// required temp > existing temp basal
        rT['reason'] += "temp " + str(currenttemp['rate']) + "<" + str(rate) + "U/hr. "
        #eturn tempBasalFunctions.setTempBasal(rate, 30, profile, rT, currenttemp)
        Flows.append(dict(title="required temp("+str(rate)+")\n> existing temp("+str(round(currenttemp['rate'],3))+")", indent='+0', adr='1140+12'))
        return                    setTempBasal(rate, 30, profile, rT, currenttemp, Flows)

