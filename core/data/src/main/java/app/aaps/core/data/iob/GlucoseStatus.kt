package app.aaps.core.data.iob

/**
 * added information about recent glucose pattern properties
 *
 * added results:
 *
 * duraISFminutes    past duration of BG changing only within +/- 5%
 * duraISFaverage    average BG during above time window
 * parabolaMinutes   past duration of BG approximating parabola shape
 * deltaPl           parabola derived last delta, i.e. from -5m to now
 * deltaPn           parabola derived next delta, i.e. from now to 5m into the future
 * bgAcceleration    parabola derived current BG acceleration
 * a0, a1, a2        parabola coefficients:   BG = a0 + a1 * Time + a2 * Time^2
 * corrSqu           correlation coefficient, i.e. quality of parabola fit
 */

data class GlucoseStatus(
    val glucose: Double,
    val noise: Double = 0.0,
    val delta: Double = 0.0,
    val shortAvgDelta: Double = 0.0,
    val longAvgDelta: Double = 0.0,
    val date: Long = 0L,
    val duraISFminutes: Double = 0.0,
    val duraISFaverage: Double = 0.0,
    val parabolaMinutes: Double = 0.0,
    val deltaPl: Double = 0.0,
    val deltaPn: Double = 0.0,
    val bgAcceleration: Double = 0.0,
    val a0: Double = 0.0,
    val a1: Double = 0.0,
    val a2: Double = 0.0,
    val corrSqu: Double = 0.0
)