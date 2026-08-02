# AutoISF version 3.2.1
This autoISF is an add-on to AAPS V3.4.6. master using oref1 and out of the box it behaves like regular AAPS. It can adapt ISF if glucose or its trends show certain behaviour. See the Quick Guide for details of those scenarios. The effects can be tuned individually to further improve your results if you already have a TIR of about 90%. Besides those adaptations there are other features like managing SMB settings or reacting to step counts. Last but not least it can serve as an enabler for Full Closed Looping (see https://discord.com/channels/953929437894803478/1025730692014936207 ).

The repo with the complete code can be found here:
https://github.com/T-o-b-i-a-s/AndroidAPS/tree/3.4.2.6+aisf3.2.1
Beware that in Android Studio you first start with its related master branch, wait for all the downloading and other updates and only finally switch to the above branch. More detailed build instructions are given in that repo including those for the new browser build option.

The main new features on the AutoISF side provided by the upgrade from 3.2.0 to 3.2.1 are:
* re-enabled keeping 1 month worth of logfiles
* The *States* and its *Values* are now included in settings exports and imports. This also means references in macros are now maintained during import (if previously exported by this new version).
* When *States* or its *Values* get updated behind the scenes (i.e. by macros or Kotlin code) the *States Tab* gets updated within 1 second.
* The new smoothing method UKF was added. It was developed for Tsunami by *piecycle* who previously developed the exponential algorithm. UKF is more powerful and already part of the AAPS4 prototype.

Base AAPS mainly added several fixes for patch pumps. Specifically for Dash you should read the hints from *Ruud* in discord's omnipod-dash channel like here: https://discord.com/channels/629952586895851530/866343285294104588/1533418479602892830
