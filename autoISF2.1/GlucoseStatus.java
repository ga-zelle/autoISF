package info.nightscout.androidaps.plugins.iob.iobCobCalculator;

import androidx.annotation.Nullable;

import java.util.ArrayList;
import java.util.List;

import javax.inject.Inject;

import dagger.android.HasAndroidInjector;
import info.nightscout.androidaps.db.BgReading;
import info.nightscout.androidaps.logging.AAPSLogger;
import info.nightscout.androidaps.logging.LTag;
import info.nightscout.androidaps.utils.DateUtil;
import info.nightscout.androidaps.utils.DecimalFormatter;
import info.nightscout.androidaps.utils.Round;

/**
 * Created by mike on 04.01.2017.
 */

public class GlucoseStatus {
    @Inject public AAPSLogger aapsLogger;
    @Inject public IobCobCalculatorPlugin iobCobCalculatorPlugin;

    private final HasAndroidInjector injector;

    public double glucose = 0d;
    public double noise = 0d;
    public double delta = 0d;
    public double avgdelta = 0d;
    public double short_avgdelta = 0d;
    public double long_avgdelta = 0d;
    public long date = 0L;
    // mod 7: append 2 variables for 5% range
    public double autoISF_duration = 0d;
    public double autoISF_average = 0d;
    // mod 8: append 3 variables for deltas based on regression analysis
    public double slope05 = 0d;
    public double slope15 = 0d;
    public double slope40 = 0d;
    // mod 14f: append results from best fitting parabola
    public double dura_p = 0d;
    public double delta_pl = 0d;
    public double delta_pn = 0d;
    public double r_squ = 0d;
    public String pp_debug = "; debug:";
    public String log() {
        return "Glucose: " + DecimalFormatter.to0Decimal(glucose) + " mg/dl " +
                "Noise: " + DecimalFormatter.to0Decimal(noise) + " " +
                "Delta: " + DecimalFormatter.to0Decimal(delta) + " mg/dl " +
                "Short avg. delta: " + " " + DecimalFormatter.to2Decimal(short_avgdelta) + " mg/dl " +
                "Long avg. delta: " + DecimalFormatter.to2Decimal(long_avgdelta) + " mg/dl " +
                "Range length: " + DecimalFormatter.to0Decimal(autoISF_duration) + " min " +
                "Range average: " + DecimalFormatter.to2Decimal(autoISF_average) + " mg/dl; " +
                "5 min fit delta: " + DecimalFormatter.to2Decimal(slope05) + " mg/dl; " +
                "15 min fit delta: " + DecimalFormatter.to2Decimal(slope15) + " mg/dl; " +
                "40 min fit delta: " + DecimalFormatter.to2Decimal(slope40) + " mg/dl; " +
                "parabola length: " + DecimalFormatter.to2Decimal(dura_p) + " min; " +
                "parabola last delta: " + DecimalFormatter.to2Decimal(delta_pl) + " mg/dl; " +
                "parabola next delta: " + DecimalFormatter.to2Decimal(delta_pn) + " mg/dl; " +
                "fit correlation: " + r_squ + pp_debug;
    }

    public GlucoseStatus(HasAndroidInjector injector) {
        injector.androidInjector().inject(this);
        this.injector = injector;
    }

    public GlucoseStatus round() {
        this.glucose = Round.roundTo(this.glucose, 0.1);
        this.noise = Round.roundTo(this.noise, 0.01);
        this.delta = Round.roundTo(this.delta, 0.01);
        this.avgdelta = Round.roundTo(this.avgdelta, 0.01);
        this.short_avgdelta = Round.roundTo(this.short_avgdelta, 0.01);
        this.long_avgdelta = Round.roundTo(this.long_avgdelta, 0.01);
        // mod 7: append 2 variables for 5% range
        this.autoISF_duration = Round.roundTo(this.autoISF_duration, 0.1);
        this.autoISF_average = Round.roundTo(this.autoISF_average, 0.1);
        // mod 8: append 3 variables for deltas extracted from regression analysis
        this.slope05 = Round.roundTo(this.slope05, 0.01);
        this.slope15 = Round.roundTo(this.slope15, 0.01);
        this.slope40 = Round.roundTo(this.slope40, 0.01);
        // mod 14f: append results from fitting parabola
        this.dura_p = Round.roundTo(this.dura_p, 0.1);
        this.delta_pl = Round.roundTo(this.delta_pl, 0.01);
        this.delta_pn = Round.roundTo(this.delta_pn, 0.01);
        this.r_squ = Round.roundTo(this.r_squ, 0.0001);
        return this;
    }


    @Nullable
    public GlucoseStatus getGlucoseStatusData() {
        return getGlucoseStatusData(false);
    }

    @Nullable
    public GlucoseStatus getGlucoseStatusData(boolean allowOldData) {
        // load 45min
        //long fromtime = DateUtil.now() - 60 * 1000L * 45;
        //List<BgReading> data = MainApp.getDbHelper().getBgreadingsDataFromTime(fromtime, false);

        synchronized (iobCobCalculatorPlugin.getDataLock()) {

            List<BgReading> data = iobCobCalculatorPlugin.getBgReadings();

            if (data == null) {
                aapsLogger.debug(LTag.GLUCOSE, "data=null");
                return null;
            }

            int sizeRecords = data.size();
            if (sizeRecords == 0) {
                aapsLogger.debug(LTag.GLUCOSE, "sizeRecords==0");
                return null;
            }

            if (data.get(0).date < DateUtil.now() - 7 * 60 * 1000L && !allowOldData) {
                aapsLogger.debug(LTag.GLUCOSE, "olddata");
                return null;
            }

            BgReading now = data.get(0);
            long now_date = now.date;
            double change;

            if (sizeRecords == 1) {
                GlucoseStatus status = new GlucoseStatus(injector);
                status.glucose = now.value;
                status.noise = 0d;
                status.short_avgdelta = 0d;
                status.delta = 0d;
                status.long_avgdelta = 0d;
                status.avgdelta = 0d; // for OpenAPS MA
                status.date = now_date;
                // mod 7: append 2 variables for 5% range
                status.autoISF_duration = 0d;
                status.autoISF_average = now.value;
                // mod 8: set 3 variables for deltas based on linear regression
                status.slope05 = 0d;    // wait for longer history
                status.slope15 = 0d;    // wait for longer history
                status.slope40 = 0d;    // wait for longer history
                // md 14f: append results from fitting parabola
                status.dura_p = 0d;
                status.delta_pl = 0d;
                status.delta_pn = 0d;
                status.r_squ = 0d;
                aapsLogger.debug(LTag.GLUCOSE, "sizeRecords==1");
                return status.round();
            }

            ArrayList<Double> now_value_list = new ArrayList<>();
            ArrayList<Double> last_deltas = new ArrayList<>();
            ArrayList<Double> short_deltas = new ArrayList<>();
            ArrayList<Double> long_deltas = new ArrayList<>();


            // Use the latest sgv value in the now calculations
            now_value_list.add(now.value);

            for (int i = 1; i < sizeRecords; i++) {
                if (data.get(i).value > 38) {
                    BgReading then = data.get(i);
                    long then_date = then.date;
                    double avgdelta;
                    long minutesago;

                    minutesago = Math.round((now_date - then_date) / (1000d * 60));
                    // multiply by 5 to get the same units as delta, i.e. mg/dL/5m
                    change = now.value - then.value;
                    avgdelta = change / minutesago * 5;

                    aapsLogger.debug(LTag.GLUCOSE, then.toString() + " minutesago=" + minutesago + " avgdelta=" + avgdelta);

                    // use the average of all data points in the last 2.5m for all further "now" calculations
                    if (0 < minutesago && minutesago < 2.5) {
                        // Keep and average all values within the last 2.5 minutes
                        now_value_list.add(then.value);
                        now.value = average(now_value_list);
                        // short_deltas are calculated from everything ~5-15 minutes ago
                    } else if (2.5 < minutesago && minutesago < 17.5) {
                        //console.error(minutesago, avgdelta);
                        short_deltas.add(avgdelta);
                        // last_deltas are calculated from everything ~5 minutes ago
                        if (2.5 < minutesago && minutesago < 7.5) {
                            last_deltas.add(avgdelta);
                        }
                        // long_deltas are calculated from everything ~20-40 minutes ago
                    } else if (17.5 < minutesago && minutesago < 42.5) {
                        long_deltas.add(avgdelta);
                    } else {
                        // Do not process any more records after >= 42.5 minutes
                        break;
                    }
                }
            }

            GlucoseStatus status = new GlucoseStatus(injector);
            status.glucose = now.value;
            status.date = now_date;
            status.noise = 0d; //for now set to nothing as not all CGMs report noise

            status.short_avgdelta = average(short_deltas);

            if (last_deltas.isEmpty()) {
                status.delta = status.short_avgdelta;
            } else {
                status.delta = average(last_deltas);
            }

            status.long_avgdelta = average(long_deltas);
            status.avgdelta = status.short_avgdelta; // for OpenAPS MA

            // mod 7: calculate 2 variables for 5% range
            // initially just test the handling of arguments
            // status.dura05 = 11d;
            // status.avg05 = 47.11d;
            //  mod 7a: now do the real maths
            double bw = 0.05d;             // used for Eversense; may be lower for Dexcom
            double sumBG = now.value;
            double oldavg = now.value;
            long minutesdur = Math.round((0L) / (1000d * 60));
            for (int i = 1; i < sizeRecords; i++) {
                BgReading then = data.get(i);
                long then_date = then.date;
                //  mod 7c: stop the series if there was a CGM gap greater than 13 minutes, i.e. 2 regular readings
                if (Math.round((now_date - then_date) / (1000d * 60)) - minutesdur > 13) {
                    break;
                }
                if (then.value > oldavg*(1-bw) && then.value < oldavg*(1+bw)) {
                    sumBG += then.value;
                    oldavg = sumBG / (i+1);
                    minutesdur = Math.round((now_date - then_date) / (1000d * 60));
                } else {
                    break;
                }
            }

            status.autoISF_average = oldavg;
            status.autoISF_duration = minutesdur;

            // mod 8: calculate 3 variables for deltas based on linear regression
            // initially just test the handling of arguments
            status.slope05 = 1.05d;
            status.slope15 = 1.15d;
            status.slope40 = 1.40d;

            // mod 8a: now do the real maths based on
            // http://www.carl-engler-schule.de/culm/culm/culm2/th_messdaten/mdv2/auszug_ausgleichsgerade.pdf
            sumBG         = 0d;         // y
            long   sumt   = 0L;         // x
            double sumBG2 = 0d;         // y^2
            long   sumt2  = 0L;         // x^2
            double sumxy  = 0d;         // x*y
            //double a;
            double b;                   // y = a + b * x
            double level = 7.5d;
            long minutesL;
            // here, longer deltas include all values from 0 up the related limit
            for (int i = 0; i < sizeRecords; i++) {
                BgReading then = data.get(i);
                long then_date = then.date;
                minutesL = (now_date - then_date) / (1000L * 60);
                // watch out: the scan goes backwards in time, so delta has wrong sign
                if (minutesL>level && level==7.5) {
                    b = (i*sumxy - sumt*sumBG) / (i*sumt2 - sumt*sumt);
                    status.slope05 = - b * 5;
                    level = 17.5d;
                }
                if (minutesL>level && level == 17.5) {
                    b = (i*sumxy - sumt*sumBG) / (i*sumt2 - sumt*sumt);
                    status.slope15 = - b * 5;
                    level = 42.5d;
                }
                if (minutesL>level && level == 42.5) {
                    b = (i*sumxy - sumt*sumBG) / (i*sumt2 - sumt*sumt);
                    status.slope40 = - b * 5;
                    break;
                }

                sumt   += minutesL;
                sumt2  += minutesL * minutesL;
                sumBG  += then.value;
                sumBG2 += then.value * then.value;
                sumxy  += then.value * minutesL;
            }

            // mod 14f: calculate best parabola and determine delta by extending it 5 minutes into the future
            // nach https://www.codeproject.com/Articles/63170/Least-Squares-Regression-for-Quadratic-Curve-Fitti
            //
            //  y = a2*x^2 + a1*x + a0      or
            //  y = a*x^2  + b*x  + c       respectively

            // initially just test the handling of arguments
            status.dura_p  = 47.11d;
            status.delta_pl = 4.711d;
            status.delta_pn = 4.711d;
            status.r_squ   = 0.4711d;
            double best_a = 0d;
            double best_b = 0d;
            double best_c = 0d;

            if (sizeRecords <= 3) {                      // last 3 points make a trivial parabola
                status.dura_p  = 0d;
                status.delta_pl = 0d;
                status.delta_pn = 0d;
                status.r_squ   = 0d;
            } else {
                //double corrMin = 0.90;                  // go backwards until the correlation coefficient goes below
                double sy    = 0d;                        // y
                double sx    = 0L;                        // x
                double sx2   = 0L;                        // x^2
                double sx3   = 0L;                        // x^3
                double sx4   = 0L;                        // x^4
                double sxy   = 0d;                        // x*y
                double sx2y  = 0d;                        // x^2*y
                double corrMax = 0d;
                BgReading iframe = data.get(0);
                long time_0 = iframe.date;
                double ti_last = 0d;

                for (int i = 0; i < sizeRecords; i++) {
                    BgReading then = data.get(i);
                    double then_date = then.date;
                    double ti = (then_date - time_0)/1000d;
                    if (-ti > 47 * 60) {                        // skip records older than 47.5 minutes
                        break;
                    } else if (ti < ti_last - 7.5 * 60) {       // stop scan if a CGM gap > 7.5 minutes is detected
                        if ( i<3) {                             // history too short for fit
                            status.dura_p =  -ti_last / 60.0d;
                            status.delta_pl = 0d;
                            status.delta_pn = 0d;
                            status.r_squ = 0d;
                        }
                        break;
                    }
                    ti_last = ti;
                    double bg = then.value;
                    sx += ti;
                    sx2 += Math.pow(ti, 2);
                    sx3 += Math.pow(ti, 3);
                    sx4 += Math.pow(ti, 4);
                    sy  += bg;
                    sxy += ti * bg;
                    sx2y += Math.pow(ti, 2) * bg;
                    int n = i + 1;
                    double D  = 0.0d;
                    double Da = 0.0d;
                    double Db = 0.0d;
                    double Dc = 0.0d;
                    if (n > 3) {
                        D  = sx4 * (sx2 * n - sx * sx) - sx3 * (sx3 * n - sx * sx2) + sx2 * (sx3 * sx - sx2 * sx2);
                        Da = sx2y* (sx2 * n - sx * sx) - sxy * (sx3 * n - sx * sx2) + sy  * (sx3 * sx - sx2 * sx2);
                        Db = sx4 * (sxy * n - sy * sx) - sx3 * (sx2y* n - sy * sx2) + sx2 * (sx2y* sx - sxy * sx2);
                        Dc = sx4 * (sx2 *sy - sx *sxy) - sx3 * (sx3 *sy - sx *sx2y) + sx2 * (sx3 *sxy - sx2 * sx2y);
                    }
                    if (D != 0.0) {
                        double a = Da / D;
                        b = Db / D;              // b defined in linear fit !?
                        double c = Dc / D;
                        double y_mean = sy / n;
                        double s_squares = 0.0d;
                        double s_residual_squares = 0;
                        for (int j = 0; j <= i; j++) {
                            BgReading before = data.get(j);
                            s_squares += Math.pow(before.value - y_mean, 2);
                            double delta_t = (before.date - time_0) / 1000d;
                            s_residual_squares += Math.pow(before.value - a * Math.pow(delta_t, 2) - b * delta_t - c, 2);
                        }
                        double r_squ = 0.64d;
                        if (s_squares != 0.0) {
                            r_squ = 1 - s_residual_squares / s_squares;
                        }
                        if (n > 3) {
                            if (r_squ > corrMax) {
                                corrMax = r_squ;
                                // double delta_t = (then_date - time_0) / 1000;
                                status.dura_p = -ti / 60.0d;            // remember we are going backwards in time
                                status.delta_pl = -(a * Math.pow(-5 * 60, 2) - b * 5 * 60);     // 5 minute slope from last fitted bg starting from last bg, i.e. t=0
                                status.delta_pn =   a * Math.pow( 5 * 60, 2) + b * 5 * 60;      // 5 minute slope to next fitted bg starting from last bg, i.e. t=0
                                status.r_squ = r_squ;
                                best_a = a;
                                best_b = b;
                                best_c = c;
                            }
                        }
                    }
                }
                status.pp_debug += " coeffs=("+best_a+" / "+best_b+" / "+best_c+"); bg date=" + time_0;
            }


            aapsLogger.debug(LTag.GLUCOSE, status.log());           //+pp_debug);      // drop the pp_debug when done ?
            return status.round();
        }
    }

    public static double average(ArrayList<Double> array) {
        double sum = 0d;

        if (array.size() == 0)
            return 0d;

        for (Double value : array) {
            sum += value;
        }
        return sum / array.size();
    }
}
