# AutoISF version 3.1.0
This autoISF is an add-on to AAPS V3.3.3.0-dev-a using oref1 and out of the box it behaves like regular AAPS. It can adapt ISF if glucose or its trends show certain behaviour. See the Quick Guide for details of those scenarios. The effects can be tuned individually to further improve your results if you already have a TIR of about 90%. Besides those adaptations there are other features like managing SMB settings or reacting to step counts. Last but not least it can serve as an enabler for Full Closed Looping (see https://discord.com/channels/953929437894803478/1025730692014936207 ).

The repo with the complete code can be found here:
https://github.com/T-o-b-i-a-s/AndroidAPS/tree/3.3.3.a+aisf3.1.0
Beware that in Android Studio you first start with its related master branch, wait for all the downloading and other updates and only finally switch to the above branch. More detailed build instructions are given in that repo.

The main new features on the AutoISF side provided by the upgrade from 3.0.3 to 3.1.0 are:
* Libre and G7 sensors managed by Juggluco and feeding the data directly into AAPS can be calibrated inside AAPS
* After calibration there is a transition period of 20 minutes during which reactivity of AutoISF is very much limited
* Libre and G7 sensors managed by Juggluco and feeding the data directly into AAPS can be smoothed by a 1st order exponential method adapted from Eversense/Esel
* The State Automation method contained in a PR by faldor20 is included

For details of these and other minor additions see the Preface in the Quick Guide.
