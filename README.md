# autoISF version 3.0
The autoISF add-on to AAPS V3.2.0.2 using oref1 can adapt ISF if glucose or its trends show certain behaviour. See the Quick Guide for details of those scenarios. The effects can be tuned individually to further improve your results if you already have a TIR of about 90%.

Currently the repo with the complete code can be found here: https://github.com/T-o-b-i-a-s/AndroidAPS/tree/3.2.0.2-ai3.0
Beware that in Android Studio you first start with its related master branch, wait for all the downloading and other updates and only finally switch to the above branch. More detailed build instructions are given in that repo.

The main new features provided by the upgrade from 2.2.8.2 to 3.0  are
* Addition of Activity Monmtor based on the phones step counter. It is a milder complement to Exercise Mode.
* The iobTH method for FULL-CLOSED-LOOPING is now handled internally which offers more automated adaptability than regular automations can do
* some autoISF specific variables are now accessible in automations
