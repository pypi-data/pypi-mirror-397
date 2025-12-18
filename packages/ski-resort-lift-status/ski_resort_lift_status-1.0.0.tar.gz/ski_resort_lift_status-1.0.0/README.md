# ski-resort-lift-status

* [Introduction](#introduction)
* [Disclaimers](#disclaimers)
* [Usage](#usage)
* [Development](#development)
* [Contributing](#contributing)

## Introduction

**ski-resort-lift-status** is an aggregator of ski resort APIs, providing a common interface for reporting lift closures, hours of operation, types, and wait times where available. While many resorts offer APIs for this purpose, each API is formatted differently, requiring unique handlers for each mountain of interest. Many mountains do not offer APIs at all, and require custom HTML element parsing to determine status. This library provides a best-effort attempt to abstract these differences away.

## Disclaimers

The usage of public APIs is always subject to change, and changes to ownership structures, API features, web page layout, etc. may cause incompatibilities with this library.

This library does not perform throttling, it is up to the user to avoid hammering the web servers. Libraries such as [ratelimit](https://pypi.org/project/ratelimit/) can help avoid making the webadmins unhappy.

Not all mountains will fill in every field in the `Lift` object. Each mountain's implementation will perform a best-effort attempt to determine the current information, however the details may slightly differ between mountains and the time of the year. For example:

* Some mountains include all lifts in their lift report regardless of status, while others omit lifts that are out of season, restricted, etc.
* Some mountains report all lifts during the offseason, while others report no lifts.
* Some mountains report scheduled opening times while others just have open/closed.
* Some mountains mark status as scheduled if lifts have a delayed opening time, while others report expected lifts as open at all times.

## Usage

```py
import liftstatus

# For other mountains, see list in README
mountain = liftstatus.mountains.colorado.Vail()

for lift in mountain.get_lift_status():
    print(f"{lift.name} - {lift.type} - {lift.status}")
```

Each entry in the lift status report is an instance of the following data class:

```py
class Lift:
    name: str
    type: LiftType
    status: LiftStatus # One of CLOSED, OPEN, HOLD, DELAYED, SCHEDULED, RESTRICTED, UNKNOWN
    updated_at: datetime.datetime | None
    open_time: datetime.time | None
    closed_time: datetime.time | None
    wait_time: datetime.timedelta | None
```

The following ski resorts are available for use. Pull requests are always appreciated for implementing more mountains. 

### British Columbia

| Mountain | Class Name |
|----------|------------|
|  [Cypress Mountain](https://www.cypressmountain.com)  |  `liftstatus.mountains.britishcolumbia.CypressMountain()`  |
|  [Whistler Blackcomb](https://www.whistlerblackcomb.com)  |  `liftstatus.mountains.britishcolumbia.WhistlerBlackcomb()`  |

### California

| Mountain | Class Name |
|----------|------------|
|  [Bear Mountain](https://www.bigbearmountainresort.com)  |  `liftstatus.mountains.california.BearMountain()`  |
|  [Boreal](https://www.rideboreal.com)  |  `liftstatus.mountains.california.Boreal()`  |
|  [Heavenly](https://www.skiheavenly.com)  |  `liftstatus.mountains.california.Heavenly()`  |
|  [June Mountain](https://www.junemountain.com)  |  `liftstatus.mountains.california.JuneMountain()`  |
|  [Kirkwood](https://www.kirkwood.com)  |  `liftstatus.mountains.california.Kirkwood()`  |
|  [Mammoth Mountain](https://www.mammothmountain.com)  |  `liftstatus.mountains.california.MammothMountain()`  |
|  [Northstar](https://www.northstarcalifornia.com)  |  `liftstatus.mountains.california.Northstar()`  |
|  [Palisades Tahoe](https://www.palisadestahoe.com)  |  `liftstatus.mountains.california.PalisadesTahoe()`  |
|  [Snow Summit](https://www.bigbearmountainresort.com)  |  `liftstatus.mountains.california.SnowSummit()`  |
|  [Snow Valley](https://www.bigbearmountainresort.com)  |  `liftstatus.mountains.california.SnowValley()`  |
|  [Soda Springs](https://www.skisodasprings.com)  |  `liftstatus.mountains.california.SodaSprings()`  |

### Colorado

| Mountain | Class Name |
|----------|------------|
|  [Arapahoe Basin](https://www.arapahoebasin.com)  |  `liftstatus.mountains.colorado.ArapahoeBasin()`  |
|  [Aspen Highlands](https://www.aspensnowmass.com/four-mountains/aspen-highlands)  |  `liftstatus.mountains.colorado.AspenHighlands()`  |
|  [Aspen Mountain](https://www.aspensnowmass.com/four-mountains/aspen-mountain)  |  `liftstatus.mountains.colorado.AspenMountain()`  |
|  [Beaver Creek](https://www.beavercreek.com)  |  `liftstatus.mountains.colorado.BeaverCreek()`  |
|  [Breckenridge](https://www.breckenridge.com)  |  `liftstatus.mountains.colorado.Breckenridge()`  |
|  [Buttermilk](https://www.aspensnowmass.com/four-mountains/buttermilk)  |  `liftstatus.mountains.colorado.Buttermilk()`  |
|  [Copper Mountain](https://www.coppercolorado.com)  |  `liftstatus.mountains.colorado.Copper()`  |
|  [Crested Butte](https://www.skicb.com)  |  `liftstatus.mountains.colorado.CrestedButte()`  |
|  [Eldora](https://www.eldora.com)  |  `liftstatus.mountains.colorado.Eldora()`  |
|  [Keystone](https://www.keystoneresort.com)  |  `liftstatus.mountains.colorado.Keystone()`  |
|  [Loveland](https://skiloveland.com)  |  `liftstatus.mountains.colorado.Loveland()`  |
|  [Snowmass](https://www.aspensnowmass.com/four-mountains/snowmass)  |  `liftstatus.mountains.colorado.Snowmass()`  |
|  [Steamboat](https://www.steamboat.com)  |  `liftstatus.mountains.colorado.Steamboat()`  |
|  [Vail](https://www.vail.com)  |  `liftstatus.mountains.colorado.Vail()`  |
|  [Winter Park](https://www.winterparkresort.com)  |  `liftstatus.mountains.colorado.WinterPark()`  |

### Idaho

| Mountain | Class Name |
|----------|------------|
|  [Schweitzer](https://www.schweitzer.com)  |  `liftstatus.mountains.idaho.Schweitzer()`  |

### Indiana

| Mountain | Class Name |
|----------|------------|
|  [Paoli Peaks](https://www.paolipeaks.com)  |  `liftstatus.mountains.indiana.PaoliPeaks()`  |

### Maine

| Mountain | Class Name |
|----------|------------|
|  [Pleasant Mountain](https://www.pleasantmountain.com)  |  `liftstatus.mountains.maine.PleasantMountain()`  |
|  [Sugarloaf](https://www.sugarloaf.com)  |  `liftstatus.mountains.maine.Sugarloaf()`  |
|  [Sunday River](https://www.sundayriver.com)  |  `liftstatus.mountains.maine.SundayRiver()`  |

### Michigan

| Mountain | Class Name |
|----------|------------|
|  [Boyne Mountain](https://www.boynemountain.com)  |  `liftstatus.mountains.michigan.BoyneMountain()`  |
|  [Boyne Highlands](https://www.highlandsharborsprings.com)  |  `liftstatus.mountains.michigan.BoyneHighlands()`  |
|  [Mt. Brighton](https://www.mtbrighton.com)  |  `liftstatus.mountains.michigan.MountBrighton()`  |

### Minnesota

| Mountain | Class Name |
|----------|------------|
|  [Afton Alps](https://www.aftonalps.com)  |  `liftstatus.mountains.minnesota.AftonAlps()`  |


### Missouri

| Mountain | Class Name |
|----------|------------|
|  [Hidden Valley](https://www.hiddenvalleyski.com)  |  `liftstatus.mountains.missouri.HiddenValley()`  |
|  [Snow Creek](https://www.skisnowcreek.com)  |  `liftstatus.mountains.missouri.SnowCreek()`  |


### New Hampshire

| Mountain | Class Name |
|----------|------------|
|  [Attitash](https://www.attitash.com)  |  `liftstatus.mountains.newhampshire.Attitash()`  |
|  [Crotched Mountain](https://www.crotchedmtn.com)  |  `liftstatus.mountains.newhampshire.CrotchedMountain()`  |
|  [Loon Mountain](https://www.loonmtn.com)  |  `liftstatus.mountains.newhampshire.LoonMountain()`  |
|  [Mount Sunapee](https://www.mountsunapee.com)  |  `liftstatus.mountains.newhampshire.MountSunapee()`  |
|  [Wildcat](https://www.skiwildcat.com)  |  `liftstatus.mountains.newhampshire.Wildcat()`  |

### New York

| Mountain | Class Name |
|----------|------------|
|  [Hunter Mountain](https://www.huntermtn.com)  |  `liftstatus.mountains.newyork.HunterMountain()`  |

### Ohio

| Mountain | Class Name |
|----------|------------|
|  [Alpine Valley](https://www.alpinevalleyohio.com)  |  `liftstatus.mountains.ohio.AlpineValley()`  |
|  [Boston Mills / Brandywine](https://www.bmbw.com)  |  `liftstatus.mountains.ohio.BostonMillsBrandywine()`  |
|  [Mad River](https://www.skimadriver.com)  |  `liftstatus.mountains.ohio.MadRiver()`  |

### Ontario

| Mountain | Class Name |
|----------|------------|
|  [Blue Mountain](https://www.skibluemt.com)  |  `liftstatus.mountains.ontario.BlueMountain()`  |

### Oregon

| Mountain | Class Name |
|----------|------------|
|  [Mt. Bachelor](https://www.mtbachelor.com)  |  `liftstatus.mountains.oregon.MountBachelor()`  |

### Pennsylvania

| Mountain | Class Name |
|----------|------------|
|  [Hidden Valley](https://www.hiddenvalleyresort.com)  |  `liftstatus.mountains.pennsylvania.HiddenValley()`  |
|  [Jack Frost / Big Boulder](https://www.jfbb.com)  |  `liftstatus.mountains.pennsylvania.JackFrostBigBoulder()`  |
|  [Laurel Mountain](https://www.laurelmountainski.com)  |  `liftstatus.mountains.pennsylvania.LaurelMountain()`  |
|  [Liberty Mountain](https://www.libertymountainresort.com)  |  `liftstatus.mountains.pennsylvania.LibertyMountain()`  |
|  [Roundtop](https://www.skiroundtop.com)  |  `liftstatus.mountains.pennsylvania.Roundtop()`  |
|  [Seven Springs](https://www.7springs.com)  |  `liftstatus.mountains.pennsylvania.SevenSprings()`  |
|  [Whitetail](https://www.skiwhitetail.com)  |  `liftstatus.mountains.pennsylvania.Whitetail()`  |

### Quebec

| Mountain | Class Name |
|----------|------------|
|  [Mont Tremblant](https://www.tremblant.ca)  |  `liftstatus.mountains.quebec.Tremblant()`  |

### Utah

| Mountain | Class Name |
|----------|------------|
|  [Brighton](https://www.brightonresort.com)  |  `liftstatus.mountains.utah.DeerValley()`  |
|  [Deer Valley](https://www.deervalley.com)  |  `liftstatus.mountains.utah.Brighton()`  |
|  [Park City](https://www.parkcitymountain.com)  |  `liftstatus.mountains.utah.ParkCity()`  |
|  [Snowbird](https://www.snowbird.com)  |  `liftstatus.mountains.utah.Snowbird()`  |
|  [Solitude](https://www.solitudemountain.com)  |  `liftstatus.mountains.utah.Solitude()`  |

### Vermont

| Mountain | Class Name |
|----------|------------|
|  [Mount Snow](https://www.mountsnow.com)  |  `liftstatus.mountains.vermont.MountSnow()`  |
|  [Okemo](https://www.okemo.com)  |  `liftstatus.mountains.vermont.Okemo()`  |
|  [Stowe](https://www.stowe.com)  |  `liftstatus.mountains.vermont.Stowe()`  |
|  [Stratton](https://www.stratton.com)  |  `liftstatus.mountains.vermont.Stratton()`  |
|  [Sugarbush](https://www.sugarbush.com)  |  `liftstatus.mountains.vermont.Sugarbush()`  |

### Washington

| Mountain | Class Name |
|----------|------------|
|  [Crystal Mountain](https://www.crystalmountainresort.com)  |  `liftstatus.mountains.washington.CrystalMountain()`  |
|  [Summit at Snoqualmie](https://www.summitatsnoqualmie.com)  |  `liftstatus.mountains.washington.Snoqualmie()`  |
|  [Stevens Pass](https://www.stevenspass.com)  |  `liftstatus.mountains.washington.StevensPass()`  |

### West Virginia

| Mountain | Class Name |
|----------|------------|
|  [Snowshoe](https://www.snowshoemtn.com)  |  `liftstatus.mountains.westvirginia.Snowshoe()`  |

### Wisconsin

| Mountain | Class Name |
|----------|------------|
|  [Wilmot Mountain](https://www.wilmotmountain.com)  |  `liftstatus.mountains.wisconsin.WilmotMountain()`  |

### Wyoming

| Mountain | Class Name |
|----------|------------|
|  [Jackson Hole](https://www.jacksonhole.com)  |  `liftstatus.mountains.wyoming.JacksonHole()`  |


## Development

1) Clone the project repository:

    ```
    cd /path/to/projects
    git clone https://github.com/NietoSkunk/ski-resort-lift-status.git
    cd ski-resort-lift-status
    ```
2) Install required packages:

    ```
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt -r requirements-dev.txt
    ```

3) Install package as an editable library:

    ```
    pip install -e .
    ```

4) Run tests:

    ```
    pytest
    ```

5) Build wheel:

    ```
    python3 -m build
    ```

## Contributing
If you have code to contribute to the project, open a pull request and describe clearly the changes and what they are intended to do (enhancement, bug fixes etc).

Alternatively, you may raise bugs or suggestions by opening an [**issue**](https://github.com/NietoSkunk/ski-resort-lift-status/issues).
