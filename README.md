# autoISF version 2.2.8.1
The autoISF add-on to AAPS V3.1.0.3 using oref1 can adapt ISF if glucose or its trends show certain behaviour. See the Quick Guide for details of those scenarios. The effects can be tuned individually to further improve your results if you already have a TIR of about 90%.

Currently the repo with the complete code can be found here: https://github.com/T-o-b-i-a-s/AndroidAPS/tree/3.1.0.3-ai2.2.8.1
Beware that in Android Studio you first start with its related master branch, wait for all the downloading and other updates and only finally switch to the above branch. More detailed build instructions are given in that repo.

Version 2.2.8.1 contains a bug fix for users specifying the *smb_delivery_ratio_bg_range* in mmol/l.

The main new features provided by the upgrade from 2.2.7 to 2.2.8  are
* support of Libre FreeStyle
* predictable SMB on/off when target is even/odd for mmol/l systems
* SMB on/off when target is even/odd also for profile targets
* revival of the exercise mode
* fixed readability of SMB-tab
