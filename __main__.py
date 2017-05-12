import requests
from dsl import *

#--------------------------------------------------------------------------------
#                                  QUERIES
#--------------------------------------------------------------------------------
@wcps
def q_count():
    with cov_iter(c="COV1") as c:
        return encode(count(c), "csv")

@wcps
def q_member():
    with cov_iter(c="COV1") as c:
        return encode(count(c.rgb), "csv")

@wcps
def q_op2():
    with cov_iter(c="COV1") as c:
        return encode(count(c.rgb < 0.5), "csv")

@wcps
def q_latlon():
    with cov_iter(c="COV1") as c:
        return encode(count(c[lon(0,10), lat(45,55), ansi("2010-01-31T23:59:00")] < 0.5), "csv")


@wcps
def q_cloro1():
    with cov_iter(c="CCI_V2_monthly_chlor_a_rmsd") as c:
        return encode(cast('float',
                           count(c[ansi("2010-01-31T23:59:00")] < 0.201)),
                      "csv")

@wcps
def q_clorophyl():
    with cov_iter(c="CCI_V2_release_chlor_a",
                   d="CCI_V2_monthly_chlor_a_rmsd") as (c,d):
        return \
            encode(cast('float',
                        avg(c[axis('Long',0,10), axis('Lat', 45,55), axis('ansi', '2010-01-31T23:59:00')] *
                           (d[axis('Long',0,10), axis('Lat', 45,55), axis('ansi', '2010-01-31T23:59:00')] < 0.45))),
                   "csv")

@wcps
def q_colortable():
    with cov_iter(a="CCI_V2_monthly_chlor_a") as a:
        myslice = a[axis('Lat', 30,70), axis('Long', -30,10), axis('ansi', "2009-09-30T23:59:00Z")]
        return \
            encode(
                switch(
                    case(myslice < 0.05, struct(red= 255, green= 255, blue= 255, alpha=   0)),
                    case(myslice <  0.1, struct(red=   0, green= 255, blue= 255, alpha= 255)),
                    case(myslice <  0.2, struct(red=   0, green= 128, blue= 255, alpha= 255)),
                    case(myslice <  0.5, struct(red=   0, green=   0, blue= 255, alpha= 255)),
                    case(myslice <  1.5, struct(red= 218, green=   0, blue= 255, alpha= 255)),
                    case(myslice <  3.0, struct(red= 255, green=   0, blue= 255, alpha= 255)),
                    case(myslice <  4.5, struct(red= 255, green= 164, blue=   0, alpha= 255)),
                    case(myslice <  6.2, struct(red= 255, green= 250, blue=   0, alpha= 255)),
                    case(myslice <   20, struct(red= 255, green=   0, blue=   0, alpha= 255)),
                    default(             struct(red= 255, green= 255, blue= 255, alpha=   0))), "png")

def print_them():
    print "\n".join([eval(x+"()")
                 for x in dir()
                 if x.startswith("q_")])
def getEOText(q):
    resp = requests.post('http://earthserver.pml.ac.uk/rasdaman/ows/wcps',
                         data={ 'query': q() })
    return resp.text

def saveEOImage(q):
    resp = requests.post('http://earthserver.pml.ac.uk/rasdaman/ows/wcps',
                         data={ 'query': q() })
    with open('image.png','wb') as f:
        f.write(resp.content)

@wcps
def q_createCOV():
    """
    for c in (CCI_V2_release_daily_chlor_a) return
    encode((float)
      coverage histogram over
$px x( 0 : 0 ),
$py y( 0 : 0 ),
$pt ansi( 0 : 361 ) 
values  (
add( (c[Long(-50:-40), Lat(45:55),ansi:"CRS:1"($pt)] < 100000 ) * c[Long(-50:-40), Lat(45:55),ansi:"CRS:1"($pt)]) 
/ 
count(c[Long(-50:-40), Lat(45:55),ansi:"CRS:1"($pt)] < 100000 ) +
add( (c[Long(-50:-40), Lat(45:55),ansi:"CRS:1"($pt + 1)] < 100000 ) * c[Long(-50:-40), Lat(45:55),ansi:"CRS:1"($pt + 1)]) 
/ 
count(c[Long(-50:-40), Lat(45:55),ansi:"CRS:1"($pt + 1)] < 100000 ) +
add( (c[Long(-50:-40), Lat(45:55),ansi:"CRS:1"($pt + 2)] < 100000 ) * c[Long(-50:-40), Lat(45:55),ansi:"CRS:1"($pt + 2)]) 
/
count(c[Long(-50:-40), Lat(45:55),ansi:"CRS:1"($pt + 2)] < 100000 ) 
)
, "csv")
    """
    cov_iter(c='CCI_V2_release_daily_chlor_a')[
        
    ]
    with cov_iter(c='CCI_V2_release_daily_chlor_a') as c:
        return \
            encode(cast('float',
                        new_cov('histogram', px=axis('x', 0,0), py=axis('y', 0,0), pt=axis('z', 0,0))
            ))



#print postEO(q_cloro1)
#print postEO(q_clorophyl)
saveEOImage(q_colortable)

print q_colortable()
"""
for $c in ( M1, M2, M3 )
where
    some( $c.nir > 127 )
return
    encode( abs( $c.red - $c.nir ), "hdf5" )
"""

"""
with coverage_exp('histogram',  # There will also be coverage_const
                   px=axis('x', lo, hi),
                   py=axis('y', lo, hi),
                   ansi=axis('ansi', lo, hi)) as (px, py, ansi):
    # values(?) --> maybe not needed
"""
