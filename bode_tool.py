import sys
import json
import base64
from io import BytesIO
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageTk as _ITk

_WIN = sys.platform == "win32"

# ── Embedded app icon (base64-encoded PNG) ────────────────────────────────────
_ICON_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAtaklEQVR4nO2de5wcV3Xnf7equqtf"
    "093TPS9rRjN6S7YsybJkjN/Y2CYxEOPFGAPh4YXdQJbPJlmSXZIsm08S8tnNxsmSjbMEYmzHEGdZ"
    "wI4J2IAdg2QZbGzJ8ktvWSNpNJpnd09Pv+u1f/RMT1d3VU91d/X0Y8738+nPzD1V99a5t26dulV1"
    "z7kMTWZwx51as3UgiGZx4Y0nWTOPv+IHpwueIMxZaYOwIgeji54gqmcljEFDD0AXPkHUTyMNQUMK"
    "pgufIOynEYbA1gLpwieIxmOnIbClILrwCWLlscMQcPUWQBc/QTQHO669ugwAXfwE0VzqvQZrGkLQ"
    "hU8QrUctjwRVjwDo4ieI1qSWa7MqA0AXP0G0NtVeo5YNAF38BNEeVHOtWjIAdPETRHth9ZoVGq2I"
    "FRjHARrZGIJYaZZ9a9jouz/jOIR6Rxp5CIJYtbz+7FcqXuMVN67E0J8xhlDfOkSmz9Y1CmC8AE2R"
    "G5Kn0n5m24zkpbKKacbB5+9BIj4DaKqV6limlrayms+utjKSm6Yb2FaV9LMjT0P7lqog1DtS0QiY"
    "PgKs+HO/pkGrxwDUkN9qnkr7mW0zkpfKKqUZFuR1tks1OtuRz662MpKbpRvZVpX0syNPI/vW4g11"
    "aOcHtLHX/9nQCNQ9FZggiPbF0ADQW3+C6CzMrmkaARDEKqbMANDdnyA6E6Nrm0YABLGK0RkAuvsT"
    "RGdTeo3TCIAgVjGFeQDNvvuHr/ocGOdYSBWpUvK90yzFGIOmVpoEUl4mYxy0sokjWtFuC/txnEHZ"
    "JWWUfpdlbCF/sY4cNFUp3kmfj7GCPgyAw+mGM5de2KW4fM3w33JBSV1UGZoqAZoGVcnl04oETZWX"
    "fnIaqpSCmkvl/0opaEq29CBEGzO4405tMXaA7b4AvOCEU/QAANLJmOV83sGrwASX3eq0Pa3QIpoq"
    "Q8nMQclEIadmoaQjkJMzyMXHIM2dh5KJNltFokZsNwBO0Yt0MgqX2w/G8fo73gKMseKE3SoQNsM4"
    "AYInDMEThhjaVLZdzSWRi40iM30MucgJZKaP50capeUwDoyVP3ValZulF2VGZdiBmX525Km0XzXt"
    "ZdQ2Glt+UC8AKzv8d3uD8Pi6V+pwxArAOb1w9W2Hq287AEBTcsjNHEVu6jXkpt8CFh8hSh95FrEq"
    "r5AWBBFef9iuKlnTz448lfarpr2Wa6sSFh8DbB8BSNkk3N4gABje/dPJGDKpOZ2iod4RZCOnwXgn"
    "dP5JusFBpZECW3rmrjCiYLA68rC+n9Fx2WK+wglgZcXm05zBSVv6n+M4qGXvHvSFMNM2KjkY48A4"
    "HowTAE4A4x2Nu2PyToj9uyD274IqZ5A8ewDzp5+BkpiAauDcwvGCJblZmjEOXn8YyfiswTud+jHT"
    "z448lfaz2i5GMo4XoKoKQr3DFY9vuwGQ5RxkOVdxH53TwsLfyf1/VpcjR9ueJJM0Yxx8gV4k5qZt"
    "79RLx2F6g8A5wDnc4Bwe/c/pA+/uhuAJ5/+6w+BdAWvHElzo2ngrujbeivTEa4i+8W3kYmd0+2ia"
    "aljHUnm1abuopVyreSrtZ7VdjGT5F9PLH78lAoIQzULLP6urEjQ5DQBQ0uZ7FxsozuGFwz8ER2AI"
    "YnAdxN5tcPqHKh7NPbAL7oFdSJ5/EZHXvgk1Ow+xZwsEVwByZg7ZmROG7w6IxiE0+/Mf0Z6oUhLZ"
    "2ePIzh5HYkHGiX54BnbCvWYv3ANXgBNEw7zete+EZ80eaJoCrujLj5KNY/7UM4gdfQLQyh8fCXsZ"
    "3HGnRiMAwjbUbBypsReROHsAjBfhXXsN/JvfA2dwXdm+jHeAwaGT8aIfwe0fhBjehMkDf7FCWq9u"
    "aCYg0RA0JYvE6M8w/szvY2Lfl5GZPWG6b9CjT7sHdiF46V0N1pAAyAAQK0Bm6i1MPPdHmH7pb3Qv"
    "qi5dw/DY50T84AtuPPY5EZeuWfpy0bXpNoBzGBVH2EjrPAJwwtInMU3LPwMyXv+da/HNZql88XOj"
    "oVzLl11Msbz4DYiafzMOjjdQsES+qCOYvvyC7ly5vFRHTgDUojoV66Pbv8hOW6mTTm5QJ04AFAO5"
    "rk4GcqM6lZ6n0joVnQ81l9R9evzSnU4M9+TTwz0c/uudTnzsq/k5A7zohxjegvTEa0vHXGyfQp0W"
    "0ozLHyvfYNXXqbh9q6xTod1L5SjKW0zpeSqrk4XzxHgAJXJOANTS87T8JLuWMQCBze8tVCYbHUX6"
    "4kG4B66A2L2usE9m+ggy00fhXXsNHL7+gjw1fhDy/Bi6NtwCXvQX5ImzByAnJxHY8t78564F4qef"
    "gSqlENj6ft0c/9ixJ8E5PPBvvK0g01QZ8yd/CMHbB9/I9QW5ko1j/vQzcASH4e6/oiCXEpNInjsA"
    "MbwFYnhrQZ6NjiI79ZquTozjkJ58s1Anp/+Sgj7pi68CWhK+DbeAd/os1ym47U5duxrVCZqK2NEn"
    "TOvkDI7As2aPpTqVnqfSOhWfJ01b+uQZ9KBw8S8y0sMh4AbmFr5ECN5egBMKdVr0yVisU2Dze/Lt"
    "xRgcDhGJ2D9VXSdXz1a4ei+ruU6p8YPIxUbL+l5q7BfIxceXPU+ldbJynlQpifjJH+nqxDgOufjF"
    "Qp3c/ZdDkyUg+hoqwZr9FaAQFXhmbGkeQA0jAI7noaqasXU2scKcw6X/Vm8yAuAYoCqK4R2E4x1Q"
    "i+cvLMoFp34Sj6aB45hOR44XoMq5Qp04wbE0D0DT4Av0IBGPQCseptgwAuB4AaqUKa/rMndLozqV"
    "nqfSOhWfD3ffdvTf8MVC+rHPiTojcHZGLYwAAGDywP1IXzxYqFPhM+RCnTiHWJgI5PP3IBGbyPch"
    "m0cAlepkNgLgGIOqSMuep9I6WTlPHMdDlbM6eV5HqVAnTnDmowL3DCEyNWo6x6ZlRgBQ5fKpi5pi"
    "4O1Wg1w1meyjygbbtHIZLxjLzfYH8p2lTC7odWRYmqyhKYDKlvIsdkpNMZ7QUalOy+nITORm+xfE"
    "RnVC5ToVnY/s7Ako2XjhTvmnT+YKjwFnZ1R8+Un9BDL/ptuRnjhc1CbF9dOWzh/jij4b1lAno/a1"
    "WCfD/YGFPoPlz5NRnRYxO09GcoalNlg8TwYzcUtpHQNAdD6qhPlTzyC4/YMAgKPjGj761axu2F+M"
    "e2Anet/xm5h+6QEYX3VEvdj+FcDr74HL4wfH0xtcopzY0SfyL/aKMLr4F/EOX4vQlfc1WKvVi+0j"
    "AFVVFt70mltsQ3dgxi0t8FAD7eqyaZZupItrLW1lNd+ybQUZUy/8JQKXfgBdG2/VvThTsnHIiUmI"
    "4c26fP6Nt0FJR5A4+RS5A5vIa3UHrvsloOAQ4XIvncTkfN4jy+PrRipRHijCzB04l03VowY6wmWz"
    "JC0IImS5AdF4amkrq/mqaStOgBBcD87hgyolIMfOAKoM72UfgWvw6rLs868/gtzkYcPyGtZWRnrb"
    "mafBfcspehr7ElCWskhI04W0y+MHx/GQJOOTYeYOnF/XjbwBi70BG+XiWktbWc1XdVtFL5bJEy8+"
    "gJ6rGbxD79Dt6r3sI0hMn0IuekZXHrkDt5A7cCYVX3YfI3dgaGpd7sDt6rK5nDtrI1xcay3TSj5b"
    "2kpTMfPSAxDcX9I9DnCCiN5rv4CLz/4BlEyM3IEryKy6A9NUYKIl0VQJ0y9+BXJyWicX3N3ofedv"
    "Fc38I+qBDADRsqjZOCZfuB+qpP9M4Ordhu4d9zZJq86CDADR0khz5zD9y78tkwe2vg/uNXuboFFn"
    "QQaAaHnS4wcRO/pkmTy8599D8A00QaPOgQwA0RbE3vp/yEwd0ck4hzv/PqB0vj1hGTIARHugqZh5"
    "+W8hp/VzS8TudQhefk+TlGp/yAAQbYOajWP6F39dFm4+sOW9cIS2NEmr9oYMANFWZGePI3bk8TK5"
    "7/KPgXN2NUGj9oYMANF2zB37Z2Smj+lknBhAeO+/a5JG7QsZAKL90FRM//JvoeaSOrFnzR50bbi1"
    "SUq1J7YYAKfLC1+gN18gJ8Dt7ab1/4iGoqRmEHn14TJ5966PQfD2NUGj9sSW7ye5TBKC4AQAOF0e"
    "ZFJzEBwiBIcI2cApiNyBl093rDuwjasDp8dfRmJ0H3zrbirIOMGFnqs+h8l9X4ZdQUTatW9ZXh24"
    "WoxcgK1i5g7s8/fUosoSbeyyaZZu2Iq3reIOXK3cIJ19+ym4+3eAd4cKYlfvNvTs+CAy5/ZV1tUq"
    "ndC3TKjJAJS6ADucbggOEQ6nG7lMCi5PAIzBMB4AuQOTO3CtcrO0/PLfof/GP9Dl9Wx6L2KjL0Ce"
    "v1hRXyu0bd9aKXdgKZeGlFty2Egnyy/8Ysgd2Fq6Gh2roeXdgU3kZunM1FtIn9sP9/CNhW2Md6Jn"
    "72dx8ad/ZMktthLt2rfIHZhYNaRO/gDS/IROJoY3IbD1/U3SqD0gA0B0BmoOs698rezOGNx+Nxz+"
    "tU1SqvUhA0B0DNnZE4if+KFOxjgBPVf9hn7xD6IAtQrRUcTe/A5y8TGdTAxthH/zrzZJo9aGDADR"
    "UWiqhJlf/p3Bo8CHIHj7TXKtXsgAEB1HLnoa8RNP62ScIJKvgAFkAIiOJPbWdyAlJnUyd992+Nbf"
    "0iSNWhMyAERHoilZzL7y92Xy0K6PgXeRn8oiZACIjiUz/Rbm335OJ+McHoT3fLpJGrUeZACIjib6"
    "+j+WhRHzrNkDz9A7m6RRa2G7O7DgcMHbFYbo8tlRNEHUhSqlMHvoG2Xy8O5PUQQhNMAdGNCgaWpF"
    "V0hyB14+Te7A1ttrubbKXHwVyfMvwrt26a7PuwIIXfEJzL781Yr1Wa5O9ebpOHdgWcpClrKFRULV"
    "kgCO5A5M7sA1yyukl2ur7Ns/gLt/BzintyDzjVwPdeZ1SJETFavUEX3LBNvdgTVVgeB0g19wRyyF"
    "3IHJHbhWuVnaWltNQz38KHre8Tmd1L31g4g980VoSq6mOtWbpyPdgWXZvDEBcge2mq5Gx2roNHdg"
    "q/olzu6Hd/hauAd2FWQOXz8Cl34A0Tf+b011qjcPuQMTxAoye+ghqLI+TJ1/y/vgCFS+U3YqZACI"
    "VYWcnELsyPd0Msbx6NnzGRSNR1cNZACIVUf8xFPIxc7qZGJ4M7o2rr6Q4mQAiNWHpmDm4N+XPUd3"
    "77h31U0TJgNArEpykdOYP/WMTsY5PAjt/lRzFGoSZACIVUv0zW9DTulD2nuH3gH3mj1N0mjlIQNA"
    "rFo0OY3Iq4+UycO77wMTXCuvUBMgA0CsalLjryB14WWdTPCE0X35PU3SaGUhA0CsemZffQSqlNbJ"
    "uja9B87ujU3SaOUgA0CsepR0BNE3v62TMcahZ+9nAMY3SauVgQwAQQCYP/UTZGdP6WTO4LqOjyZs"
    "iwFwefxw+7rhFL20PDjRpmj5uQElDmzB7XeD9/Q2SafGY4szUCYVB+M4uNx+cDxPy4ObyCkeQHPi"
    "AVhFjo8hfvJpBLa+ryDjBBGh3Z/C1PN/XlVZrdC3VjQegNsTQCoRg8tTOcoKxQOgeAA1y+uIB2AV"
    "eWw/lLXvBO9Z6o/u/p0IbbkduclXrRfUan3LBFviAXQFByBLGTicLloevIKc4gE0Mx6AdeSDD6L/"
    "hi/qZJ4tdyJ65gA0KWWpjJboWysVD2A+pl+VlZYHp3gA1WxbqXgAVklPvIbEuRfgG76uIONdQQS3"
    "fwiRVx+2VEYr9C2KB0AQNRI9/E2ouaRO1rXx1o6bG0AGgCAMULJzZVGCGOMQ3vOZjlppuHNqQhA2"
    "M//2vyI7e1InE7vXwb/pV5qkkf2QASAIUzTMHHywfG7A5R8C727A15kmQAaAICogzZ3D/Kkf62Sc"
    "4EJ49yebpJG9kAEgiGWYO/o45NSMTuYZvKoj4gaQASCIZdCULGYPPVImD+/+FBgvrrxCNkIGgCAs"
    "kL54EMmyuAE9CG7/UJM0sgcyAARhkYhB3AD/5l+BMzDSJI3qhwwAQVhESUcQe+s7Ohnj+PzcgDZd"
    "U8B2d2BaHpzoZOKnfoxsdFQnE8Ob2nZNAdvdgdWcDFoenNyBq9nWKu7AZpQeN3LoGxi45Y91su4d"
    "9yJ14RWo2TnDPFbLtrKtpd2BAY2WBzeTkztwy7sDG1J6XHUe2fMvwDV8Q0HEOTzou+ozSLzxqHEe"
    "q2Vb2dbK7sC0PLi5nNyB28Md2Ip+yUP/gDW9l0NwL93MxIErETv5E2Qm32iNvtUsd2BaHpzcgavZ"
    "1mruwFb006QkIocfRd81v6WTh3bfh/Ef/15L9C1yByaIBpIaexHpidd0MoevH4FL72qSRtVDBoAg"
    "6mD20ENQFf2IN7Dt/RC61jRJo+ogA0AQdSAnpzB35HGdjHECQlfc1ySNqoMMAEHUydzxHyA3N6aT"
    "uXq3wbfupiZpZB0yAARRL5qC2UMPlom7d34MnLNylOxmQwaAIGwgO3Mc82d+qpPxYhe6d360SRpZ"
    "gwwAQdhE9PXHoGTjOlnX+ndB7Lm0OQpZgAwAQdiEmksg8to/lsnDez4NcLZMubEdMgAEYSPJs/uR"
    "nnpLJ3P6BxHY8j6THM2FDABB2Ezk0EPQVP1U3cBld0Hw9jVJI3NsMQCiywe3Nwin6KHVgYlVjzQ/"
    "jvjxf9HJON6J8JX/tkkamWPLg4mUy8DtC0KWsnC6PLQ6sImc3IE7wx3YCvMnfgjP2mvg8A0UZO6B"
    "XfCuvRapsRctld1W7sDJ+AxcHn+FXHnIHZjcgWuWt4o7sMU86eOPw7HnN3Xi8O5Pgk+PQ5PTy5fd"
    "Lu7Abm8QjDHIUm4hFgCtDkzuwNa3taM7sKU8sRfA914B7/C1S3LRD8fwLYi8+siyZbeNO3A6GStJ"
    "0+rA5A5sfVs7ugNbzRM5/CjcA7vAOb2Fbb4N78b86D7kIqfJHZggOhmzRUZ7WmSR0eZrQBAdzvzb"
    "/4rM7AmdzBlcB//mX22SRkuQASCIhqNh9uA3yhcZ3X530xcZJQNAECuANHcO8ZNP6WSc4EL3ro83"
    "SaMFHZp6dIJYRcTe+h7k5LRO5lmzp6mLjJIBIIgVQlOymF34/FdMMxcZJQNAECtI+uIhJMd+qZPl"
    "Fxm9uyn6kAEgiBUmcvgfoMoZncy/+VfhCFSetNMIyAAQxAqjpCOIvWm0yOinsdKLjJIBIIgmED/1"
    "I+RiozqZK7wFvg23rKgetrsD0+rABGEBTcXMwQfLpvR277gXnBhYMTVsdwcGNNDqwOQOXM22TnQH"
    "tpJHip5B8sxP4dvw7oKMd/oQ2vXrmH35q+3pDpxJxWl1YDM5uQOvKndgK3ly556FOngVOHHpevKN"
    "XA915nVI0ZPt5w4sCE5aHdhETu7Aq8wd2GLfUg4/it6rP6+Tu7fchbnnvgRVSlsqu6XcgWl1YHIH"
    "rmZbJ7sDW9kvee4F+NbdBHf/joLc0XUJ/FvuQLTka4FZ2eQOTBBtzOyhh6CVLDLq3/J+CEUhxRoB"
    "GQCCaAHkxARiR5/UyRjvQPjKTzf0uGQACKJFmDv+fUjz4zqZu/9yeIeva9gxyQAQRKugypg9+I0y"
    "cWjXx8E5vAYZ6ocMAEG0EJnpI0iM7tfJeFcA3TvubcjxWmfBMsbqmwXNmH6CkZ15Ku1nts1IXiqr"
    "lC76W2fLWNfZjnx2tZWR3CzdyLaqpJ8deQz2i7z+GFx928EXBxIduR6J0X3IRU9b7luwcHw2uOPO"
    "2r+92QDjOIR6R5qpAkF0NJHps9BU40+CTR8BaKqKyPTZuiYBAcDUqX3o23RTQ/JU2s9sm5G8VFYx"
    "vTBByo62saqzHfnsaisjuWm6gW1VST878jS8bzFmevEDLWAAAFRU0CqqIlU9kchqnkr7mW0zkpfK"
    "KqWXJkhpdU2QqkZnO/LZ1VZGcrN0I9uqkn525Gl431pGh455CegNr29Ynkr7mW0zkpfKlks3ilqP"
    "YyWfXW1lJG+n9mq1vmVG098BEMYwxhDqW4fI1GhD7mqdBLVV7XTMCKDT0DQNqUSUOrQFqK1qhwxA"
    "C1PqZEWYQ21VG2QACGIVQwaAIFYxZAAIYhXTEvMAGMc1ZAIHQax6Wn0iEE0FJojG0tJTgRfv/PVO"
    "42S8AK3KuG1W81Taz2ybkbxUVjHNOPj8PQuxEu0Nc1VLW1nNZ1dbGclN0w1sq0r62ZGnoX1LVfI3"
    "1wrXVfMNwCJ1TuNkNeS3mqfSfmbbjOSlskrpQoj0BkxvraWtrOazq62M5GbpRrZVJf3syNPIvmXl"
    "hkovAQliFUMGgCBWMbY/AvCCE07RA6C62VnDzgRkjSGncZBUDjkt/5M1BqzwgokEsVqw3QA4RS/S"
    "yShcbj8Yx0MzWBzEaGmwb259AV5OKttX1QBJ4yBpHHILhiGj8kipAtIqj8ziX82BlJLfllZ5pAvb"
    "8+mE4sB84ScgoTig0dJgtuejpcGqy9PIvtWwpcHqwWxpMDM4BohMhQgV4O3VJa0KSKjOop+IhOrE"
    "nCoiqrgRU1yIKS5E1fz/UcWNtCZANyKhpcGs70NLg1W3n519ywTbDYCUTcLtDQKA4d3fbGmwZuDm"
    "ZLg5Gb1IWc6TUTnEZCdmZRFTkhvTsgcTWRGTkgtTkhuTkhvTkgiFE2lpMIvbVvvSYA1bdm6llgYr"
    "RpZzNS0Ndv+Fy+BhEhxMhZNT4WRq4X8Hy6fzcgVuLv9zcYv/y3Dz+f8FC8OeenBxKgacGQw4M9iO"
    "OdP9ZiURYzk3zme9GMt6cT7rwZjsx7m0iLjiBEBLg1Ur79SlwRq17JyVOREtMw/gXyJr6/qGu2gB"
    "BaYuGYUiA+HjZfh4CV28jC5eyv8EBT4ut5BekgeF8ncR1RJ2ZBF2ZLHLGyvbNic7cDbrxdvZAE6l"
    "vDiV6cKpTBfmtJY5HcQqoeN6nKxxmFc4zCuOZfc1G2LxUBEQJISELLqFHMJOGd1cGkEhh5CQRciR"
    "Q4+QRZ8jjR5HFlyVHykCgoSdQgw7vTEgtCSPyE6cTnfheNqPI+lunOFFnERjRzTE6qbjDIAdKOAQ"
    "kUVEZBFA5ec0B88hzCXR50ij35lBvyODPkcGa8QMBp0JrHWm4ObL34UYERJyCHXN4qquWQBnABxC"
    "bMCBt1JBHEkF8EayG4eT3Uiqyxs3grACGYA6UcBhQnJjQnKj+F3iktHQ0CNkMSSmMOJOY1CYx7CY"
    "wgbXPEZcyWXfWQQFCdf5p3Gdfzp/PA04lg7gUCKEg4kwXk2GkLAw2iEII8gANByGGdmFGdmF1zP6"
    "kYQoMKwV5rDJNY+N7nlsciex2TWHS5xp09J4Bmz3zGG7Zw4f7zsDVQOOpII4EO/FC/E+HE0HoNHE"
    "KcIiZACaiKTxOJXx41TGD8SWRg3dQhbbPXHsDuWwmRvHdk/U9MUkx4DLvTFc7o3hs5ecRERy4ufz"
    "vTgQ78OBeB/SKp1iwhzqHS1IVBbxwnw/XuN6kZhbC01TMORMYbcvgj2+CK70zmJQNB4lhBw5vC90"
    "Ae8LXUBG5fDzeC+ejV2C5+P9SJExIEqgHtEWMIzlvBiLePEvkbUAgAFHGlf6ZnF11wyu6ZpG2FE+"
    "98LFqbglOIlbgpPIqhx+Md+LpyKDOJBcg+xKV4FoScgAtCkTkhtPRYfwVHQIDBq2uecWXhZO4XJP"
    "rOzTpMipeFdgEu8KTCImv4EfRQfx/cgQjqcDzakA0RKQAegANDAcTQdxNB3Eg5Ob0S1kcXNgArcG"
    "L2KvbxZ8iTEIChLu7R3Fvb2jOJ7244mZtfhBdIjeF6xC6Ix3IFFZxOOzI3h8dgRBPoubg5O4LTiO"
    "q3yzZSODre44vrj2LXx+zXF8PzKEb0+vw1jOa1ww0XGQAehwYoqIJ2aH8cTsMPodabw3NIb3hy5g"
    "WEzq9vPxMj7aO4qP9o7iwFwvHptej5cSPaBYDJ0NGYBVxKTkxkOTm/HIzDbsdE3j10Ln8Z7ucbg4"
    "vdPI9YFpXB+YxlupAB6e3ISfzfXT3IIOxRYD4PX3QJFzyGXTgKZBdHeBMSCViNpRPGE7DIeTIRxO"
    "hvCV8UtxZ+g8PtRztuzT4nbPHO5ffxBvZ3x4ZHIjfhIfhv2+dkQzscUAqKqyEI1Eg9PlQSY1B8Eh"
    "QnCIkKXyD05GEYHAuKXorjXQrlFbmh0RaF514Vszm/HYzCbc4J/EPT1ncHXXjG7/Da4E/mTkNfxG"
    "7iS+PrEFT0eHoJqMCCgiUHV5mh0RiA3uuLPqq05wiHC5/YV0cj4fiMHj64aqKsimExAcIjRNLTMA"
    "ZhGBclnrQTkM6YSoLQYRgWS5AV/sl6n3FucMPhp4HTd6Rg09Hc/kgngodiWeT42g7B1BEyMCNaSt"
    "KulnR54G9y2n6EFkatQ89HgtBqAUl8cPjuMhSVkoUm7ZR4DSEUCodwSR6XN1LQzStlFbWjgi0Ig4"
    "j0/2ncYd3WOGTktHUgH8n4lteHG+F4uGgCICVZdnJSICVTIAtjwCZFJxXTqdrPzsbxQRCJpaV0CQ"
    "do3a0soRgUYzXvzxuZ342sVN+HT/KfxaWG8ILvPM4YENL+HFeA/+avwynM50UUSgKvM0OyIQrQtA"
    "LMuE5MGfje3EPSduwY+ia8q2v9M/g3/auh+/P/QGgjxNMm4nyAAQljmf8+EPz+7Gh4/dgJ/N9eu2"
    "8Qy4u+ccntj6LD7eexoOZi0ICtFcyAAQVXMq48cXzuzFp09eg7dSel8CHy/jtweP4bvb9uMG/2ST"
    "NCSsQgaAqJnDyRA+eeI6/LezuzCVE3XbhsQUvrLhFfzl+ldwibPOLzxEwyADQNSFBoYfRodw17F3"
    "4WsTm5FR9au3vCswie9u24f7+k7RY0ELQgaAsIWMKuDrE1tw94l348fRS3TbXJyKz685jn/a/FO8"
    "wzdjUgLRDMgAELYyKbnxB2evxGdPXY3RjN6rcERM4qubXsJ/HzmEXkemSRoSxZABIBrCy4ke3Hv8"
    "BjwwvhUZVd/Nbu++iO9t+xk+0nsGPHkXNBUyAETDkDQeD09twt3HbsJPY/rPhl5ewe8OHsE3t76A"
    "HZ5IkzQkyAAQDedizoPfHd2L3x69GmNZt27bVnccD218Hn849Dr8fOU1JQn7aZl4AAJTgAVvQE1j"
    "kMFBgApWNPVU1RgUcBCYqvMcVDRuoQy9XNY4aGBlb5/zcsDBFKhF2ySNA1sopxgFAhg0nVwDg6xx"
    "4KCBLypjUc5D1cs1BhXQ1YljDDLUQp34In0Wve3yx1wqZ/k66XU3qhPHGLLAMnUqlxvVqfQ8ldap"
    "+Hz8Yr4f98zdhM/0n8TH+07DUXT7+Tc953FzcAIPjG/FD6ODABhU8AC0Qp04xqAypVCnxfPHmAbH"
    "QhvVUieuqI9VWydF46CClcnVhbXslztPpXWycp4Y45ADdHXiGIPC1EKdhJK+bUbLGIBf7z1TaKxj"
    "qQD2x/txrX8a2zxLK/AeTIRxMBHG7cFxDIlL35b3z/XjRC6Mu8Ln0C0s3UWeigxiLOfNl10U9OI7"
    "MyNIKAI+1XtaN3/64cmN8PEyPtRztiCTVA7/MLsNg84U7ghdKMijshPfmVmHza453NA1XpCPZT14"
    "KjqEXd4IrvRMFeTHUgEcSA7q6sQYh1fmuwt1WuvKFPTZHx/ABfThrtBZBIWl6bXL1em+/tO6djWq"
    "kwwBD01sMK3TFnccNwaWJvFUqlPpeSqtU/F5en5+DY4mfZiSXXh8dgTX+6d0MQi6BQlfGn4Tnxk4"
    "hQPxPvz91GWIqyjUiTEOmqYW6nRP73lomgoGBoiT+PrcmqrrdIUvij2+2ZrrtH+uH8fSgbK+96O5"
    "YZxLu5Y9T6V1snKe5hQXvj09rKsTYxzOZ1yFOu3tiiKnMnwfG1GJmrwBnS4vnKIHiblpcJyg8/5z"
    "uf0AA1RFtuTiyxhDqG8d4tOnC96ANY0AeAc4NVfVCEAUOJ0HlekIgBOhKZLhnUXgeTA1VyZ38Byg"
    "Li3moWkMKu8Ep+SW7iy8AFlWlkYAPF/QR4UAT6APmfgkoNk8AuAFZGWt6rulUZ3K7pYldSo+Hxrn"
    "hKwoRXINtwUu4rcGj6GnJKy5rAGPzWzE1y9uhLwwwlv0eFusk3Ph/DHGwefvRXQuAmiK/SOACnUy"
    "HQFwTiiKsvwIoKROVs4T4x3Iyap+BMALUBRlaQQg8FBVBf7ejfZ7A+YySQhCfo370gAgjOORTkbh"
    "9nUDJgbAKCCIDAcWHwHA8l6CSukrigpyjnFQSquzsL9sUo6cP82lqkCGfjILxzhojC+TMwZojIcC"
    "R5lcZYL+/faijmxJRw4CVMYKddKK9FkM7qBAgFas/7J1KtextE4cBDAmG9aVsfxZMJIb1an0fJTW"
    "qRiO8WBM08mfnhvBgdQwPtv3Ju4OjxYiGAsM+ETvadweuID7L1yOn8UHwMEBFayoTvn2YuAggc/f"
    "TautE7i66mTWJxfrutx54hbrUMV5WpRrJuWo4BbaZvlXfJYMgFEAkFoxCwji8/fUXCaAtg7aYJYW"
    "BBFef3h5/aqllraymq+GttIYw1cTffjX3Az+U/jn2CYuTRYacGZw//pX8IvUWvx19BpMSN2G5TWs"
    "rSrobUuelepbZoev5RHA4XTD7Q0gnZyDIksGjwAMqiKZPgJQQJDl060QEKSWfPW2FQcNd4XP4vOX"
    "HEUXr983o/L4xuRmfHM6/1hAAUHMZQ0NCCLl0pBySy9vigOAZNJxoyw6KCCItXQ1OlZDrWVayVdv"
    "WykAvjszjOdi/fidwWO4o3ussJ+LU/AfLjmGO7rP43+MXY5D6QEKCGIio4AgRFsTkUX80dge/Map"
    "q3GmZErxelcSX9v0Ev5s7StYQ56GdUEGgGhpXkn04N7jNy5MKda/xLs9eAHf27YP//GSI/BxFImo"
    "FsgAEC2PrHF4eGoTPnziZuyf69Ntc3IqPtF3Gv84+F3cEz6Dku8UxDKQASDahnHJi985sxe//fbe"
    "Mk/DAJ/Ffx56E9/eth+3BC7WtcbEaoIMANFmMDwf78eHj92I/zm+AzFZPwdjnSuJv1h/CN/acgA3"
    "+icBMgQVIQNAtCUyOHxndgPuPHozHp3aiJym78rbPHH8rw2v4NEtL+DarimQITCGDADR1iQUB/73"
    "xcvwiQsfxNPRQagl1/l2zxz+ZuPLeGTzz3FzYIIeDUogA0B0BBNyF7507krce/xGPBsbKNu+wxvD"
    "/esP4rvb9uEDoXMUn3ABMgBER3E604X/MroHHzl+fdnaBUD+HcGXht/ADy77Ke7rO7XqFzIhA0B0"
    "JCfSAXzhzF78+vHr8Fysv+zRoMeRxefXHMfT25/Dnw6/ip2eCFbje4KWiQdAEI3gaDqI3xvdixEx"
    "gY/3vY33dl+As8g/38mpuCM0jjtC4ziR7sL3Zkbw49gazCuOCqV2DjQCIFYFZ7M+fPn8Trz/yM14"
    "eHIj4nL5vW+Lex6/v/ZN/GT7s/jzdQdxg3+y4ycW0QiAWFXMyC48cHEbHpzYjNu7x3FPzygu9egd"
    "2JyciluDE7g1OIGo7MRPYoN4NtqPw8mQLn5EJ1CTASiOCCQ4XBBdXshSFtlMouqIQATRDDIaj+9H"
    "1uL7kSFs98zh7vBZ3N49Dhenv+N3Czl8uOcMPtxzBhHJiX3xfjwXG8DLiTAkjTcpvX2oOyIQoOXj"
    "si1EsKk1IhAYV9c3Wsa4gg5256m0n9k2I3mprFK69K+d1NJWVvPZ1VZGcrN0vW11JB3Cn4yF8Ffj"
    "l+PdwXHc0T2GPb7yUOUhRw53hc/jrvB5JBQBL8334hcLv0nJY6lOy9XRyjarfUtjNgUEMYoI5PYG"
    "kEosxQFwefzIZZIQ3f6CAUgXbV/ELCJQ3aOFTojaYhARSJYb8JmqxSICWZZXSNvdVgPCPG7znsZt"
    "vlMYdiwf4+JsLoCXM4M4mF6DN7L9SGiuluhbTtFTMSBI3RGBNFWB4HSD5wUk52cpIlAFOUUEst5W"
    "RnKzdGMjAmnY5EnjJt8YbglexFb38sYAyC+h/mqiG4eTYbyaDGFKchvu1xERgWR5KaIrRQQyl1NE"
    "IOttZSSvpf3s4HTGh5PJTXhwchMGnSncHJjA9f4pXOGNwMEZ99lNrjg2ueKFMN/TkogjqQCOpgI4"
    "ms7/nZVdTY8IRF8BCKIKLuQ8+Nb0BnxregPcnIy9vlm8s2sa13TNYMSVNM3X68jipsAUbgosrasw"
    "mXPhVNaP02kf3s74cCbjw9uZLqTUlbssyQAQRI2kVQHPx/vxfDw/5XjAkcJuXwS7vVHs9kWwwZWo"
    "mL/fmUG/M4PruqZ08omcC29nunA+58NY1oWxrBcXch5cyHqQsfnLAxkAgrCJCcmDp6MePB0dAscL"
    "8COFXd4Idnpj2OaZw6XuOQQEadlyBpwZDDgzAKbLtk1LIi7kvLiYdWFKWvrNKF5MZh2YkcTytQsq"
    "QAaAIBpETHFiX3wA++KL3okaBp1pXOqew6WeGLZ54tjgSqDPkbFcZq8ji15HFld4jbcrWj6g6rTk"
    "wkXJgz9PratYHhkAglgxWH4on/Pg2blLAOTf1nuRxnpxHhtdCax3JbDRNY91C4aBq3LiIc+WjMSI"
    "mgKW+bpOBoAgmsy84sDrqRBeT4V0clFg6OfnMeRMYVBMYciZwpCYwqAzjT5H2tLjxHKQASCIFkXS"
    "eJzL+nAu6wPml+SL3/xdTEGvI4M+ZwYDYg49fAp9jgz6HGmEHRJcvIXlwS+88WRNk4EIgmguGY3H"
    "+ZwX53NecOnyiUCaqiDUZ57/whtPNmCiOUEQbQMZAIJYxZABIIhVDAfknwWarQhBECvH4jXfOl8B"
    "GKsv1gpjei9DO/NU2s9sm5G8VFYpXfS3zpaxrrMd+exqKyO5WbqRbVVJPzvyNLBvwcLxm28AFpQM"
    "9Y40WZHWJNQ73GwV2gZqKxMqxBzQmYhmfQ5kHFdXLAAAmDq1D32bbmpInkr7mW0zkpfKKqYLcRLO"
    "1t02VnW2I59dbWUkN003sK0q6WdHnob3LcagqXq34OJH/uaPAIAyBWtBVaSq4wlYzVNpP7NtRvJS"
    "WaX0UpwEra44CdXobEc+u9rKSG6WbmRbVdLPjjwN71vL6KD7CtDOLwO94fUNy1NpP7NtRvJS2XLp"
    "RlHrcazks6utjOTt1F6t1rcWKb3Gyy54mhXYGjDGEOpbVzGcE5GH2so6pQagbB5AO48COglN05BK"
    "RKlDW4DayhpG1zZNBGph0slYs1VoG6itasPQANAogCA6C7NrmkYABLGKMTUANAogiM6g0rVccQRA"
    "RoAg2pvlruFlHwHICDQfp+iF6O5qyDqBnQgvOOFydzVbjaZj5dqlHtUi8LwDXYE+cLwDvOCE2xuE"
    "2xvMb2QMUi4NXnA0VcdWolJ7KXKOPglaxJIBoFFA41GK1lJ0il6kkzFoqgrG8YCmweF0Q5HrDwLZ"
    "KVRqL44XwAtOGMxzWzVYvWYtjwDICDSPXDaJbHq+IevedSKqIiOViAB1LDffzlRzrVb1CEBGoHFw"
    "HA+H6IbL7YOUTcHtDYJxHDR1+ciuqxFqL2OqvUZruqDJX4AgWo9abtB13dHJEBBE86lnZF7XVwB6"
    "JCCI5lLvNVj3Z0AyAgTRHOy49my9eOmRgCAaj5033YbcvckQEIT9NGK03dDhOxkCgqifRj5mr8jz"
    "OxkCgqielXi/tuIv8MgYEIQ5K/1Svelv8MkgEKuZZn9F+/++3sIlcGX2QgAAAABJRU5ErkJggg=="
)


# ── Recent-files persistence ───────────────────────────────────────────────────
_RECENT_MAX  = 8
_RECENT_PATH = Path.home() / ".bode_tool_recent.json"

# ── Data constants ─────────────────────────────────────────────────────────────
COLUMNS    = ("freq", "amplitude", "phase")
COL_LABELS = ("Frequenz (Hz)", "Amplitude (dB)", "Phase (°)")
FREQ_UNITS = {"Hz": 1e0, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9}
AMP_UNITS  = {"dB": None, "V": 1e0, "mV": 1e-3, "µV": 1e-6, "kV": 1e3}

# ── Color palette ──────────────────────────────────────────────────────────────
P = {
    "header":     "#1b2d4f",   # navy sidebar/header
    "header2":    "#243860",   # slightly lighter navy
    "sidebar":    "#1b2d4f",   # left panel background
    "bg":         "#f0f4f8",   # main content background
    "card":       "#ffffff",   # white cards
    "border":     "#dde3ee",   # subtle border
    "accent":     "#3b82f6",   # primary blue
    "accent_dk":  "#2563eb",   # darker blue (hover)
    "accent_lt":  "#dbeafe",   # light blue
    "text":       "#0f172a",   # primary text
    "text_inv":   "#e8f0fe",   # text on dark bg
    "muted":      "#94a3b8",   # muted text on dark
    "danger":     "#f43f5e",   # delete / danger
    "danger_dk":  "#e11d48",
    "success":    "#10b981",
    "warning":    "#f59e0b",
    "row_a":      "#f8fafc",
    "row_b":      "#ffffff",
    "input_bg":   "#f1f5f9",
    "sep":        "#2e4470",   # separator on dark bg
}

_SANS  = "Segoe UI"   if _WIN else "Sans"
_MONO  = "Courier New" if _WIN else "Monospace"
FONT      = (_SANS, 9)
FONT_B    = (_SANS, 9,  "bold")
FONT_LG   = (_SANS, 11, "bold")
FONT_SM   = (_SANS, 8)
FONT_XS   = (_SANS, 7, "bold")
FONT_MONO = (_MONO, 9)

# ── Button icons (generated via Pillow — no font/emoji dependency) ─────────────
_ICON_REFS: dict = {}  # keeps ImageTk.PhotoImage alive (GC would blank the button)

def _icon(name: str, size: int = 14) -> "_ITk.PhotoImage":
    key = (name, size)
    if key in _ICON_REFS:
        return _ICON_REFS[key]
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)
    c   = (255, 255, 255, 210)
    s, h = size, size - 1
    cx = s // 2
    if name == "chart":
        d.line([0, h, s - 1, h], fill=c)
        for i, bh in enumerate([s * 10 // 14, s * 13 // 14, s * 8 // 14]):
            x = 1 + i * (s // 3)
            d.rectangle([x, h - bh, x + s // 4, h - 1], fill=c)
    elif name == "save":
        d.rectangle([cx - 1, 1, cx + 1, s * 5 // 10], fill=c)
        for j in range(s * 5 // 10 + 1, s - 2):
            sp = j - s * 5 // 10
            d.line([cx - sp, j, cx + sp, j], fill=c)
        d.line([1, h, s - 2, h], fill=c, width=2)
    elif name == "import":
        # folder outline
        d.rectangle([0, s * 3 // 10, s - 1, h], outline=c)
        d.rectangle([0, s * 1 // 10, s * 2 // 5, s * 3 // 10], fill=c)
        # arrow pointing down (data coming in)
        d.rectangle([cx - 1, s * 4 // 10, cx + 1, s * 7 // 10], fill=c)
        for j in range(s * 7 // 10 + 1, h - 1):
            sp = j - s * 7 // 10
            d.line([cx - sp, j, cx + sp, j], fill=c)
    elif name == "export":
        # folder outline
        d.rectangle([0, s * 3 // 10, s - 1, h], outline=c)
        d.rectangle([0, s * 1 // 10, s * 2 // 5, s * 3 // 10], fill=c)
        # arrow pointing up (data going out)
        top = s * 2 // 10
        d.rectangle([cx - 1, s * 5 // 10, cx + 1, h - 2], fill=c)
        for j in range(top, s * 5 // 10):
            sp = s * 5 // 10 - j
            d.line([cx - sp, j, cx + sp, j], fill=c)
    elif name == "trash":
        d.rectangle([s // 4, s // 4 + 1, s * 3 // 4, h - 1], outline=c)
        d.line([s // 5, s // 4, s * 4 // 5, s // 4], fill=c, width=1)
        d.rectangle([s * 3 // 8, 1, s * 5 // 8, s // 4], outline=c)
        for x in [s * 2 // 5, cx, s * 3 // 5]:
            d.line([x, s // 3 + 1, x, h - 2], fill=c)
    photo = _ITk.PhotoImage(img)
    _ICON_REFS[key] = photo
    return photo


CSV_HELP = """\
Die App erkennt CSV-Dateien automatisch (Trennzeichen, Dezimalzeichen).

══════════════════════════════════════════════════════
FORMAT 1 — Deutsch  (Semikolon, Komma als Dezimal)
══════════════════════════════════════════════════════
Frequenz (Hz);Amplitude (dB);Phase (°)
100;-3,01;-45,0
1000;-6,02;-63,4

══════════════════════════════════════════════════════
FORMAT 2 — Englisch  (Komma, Punkt als Dezimal)
══════════════════════════════════════════════════════
Frequency (Hz),Amplitude (dB),Phase (deg)
100,-3.01,-45.0
1000,-6.02,-63.4

══════════════════════════════════════════════════════
FORMAT 3 — Ohne Kopfzeile
══════════════════════════════════════════════════════
100;-3,01;-45,0
1000;-6,02;-63,4
  Spaltenreihenfolge: 1. Frequenz  2. Amplitude  3. Phase

══════════════════════════════════════════════════════
FORMAT 4 — Mit Projektkommentar (wird beim Export erzeugt)
══════════════════════════════════════════════════════
# Projekt: Tiefpassfilter 1. Ordnung
Frequenz (Hz);Amplitude (dB);Phase (°)
100;-0,04;-0,57

  Zeilen mit # werden ignoriert.
  Projektname wird automatisch übernommen.

══════════════════════════════════════════════════════
SPALTEN-ERKENNUNG  (Schlüsselwörter)
══════════════════════════════════════════════════════
  Frequenz  →  freq, hz, f(
  Amplitude →  amp, db, gain, mag, betr
  Phase     →  phase, pha, grad, deg, winkel

══════════════════════════════════════════════════════
EINHEITEN
══════════════════════════════════════════════════════
  • Frequenz in Hz  (z.B. 1000 für 1 kHz)
  • Amplitude in dB
  • Phase in Grad (°)

  Spannungswerte (V/mV/µV/kV) können in der App
  eingegeben werden → Umrechnung: dB = 20·log₁₀(U)
  In CSV-Dateien werden immer dB gespeichert.
"""


# ── Helpers ────────────────────────────────────────────────────────────────────
def v_to_db(volts: float) -> float:
    if volts <= 0:
        raise ValueError("Spannung muss > 0 V sein.")
    return 20.0 * np.log10(volts)


def _btn(parent, text, cmd, bg, fg="#ffffff", width=None, icon=None, **kw):
    """Flat colored tk.Button with hover effect."""
    props = dict(bg=bg, fg=fg, activebackground=_shade(bg, -20),
                 activeforeground=fg, relief="flat", bd=0,
                 cursor="hand2", font=FONT_B, padx=10, pady=5)
    if width:
        props["width"] = width
    if icon is not None:
        props["image"]    = icon
        props["compound"] = tk.LEFT
        props["padx"]     = 8
    props.update(kw)
    b = tk.Button(parent, text=text, command=cmd, **props)
    b.bind("<Enter>", lambda _: b.config(bg=_shade(bg, -20)))
    b.bind("<Leave>", lambda _: b.config(bg=bg))
    return b


def _shade(hex_color: str, delta: int) -> str:
    """Lighten (delta>0) or darken (delta<0) a hex color."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = max(0, min(255, r + delta))
    g = max(0, min(255, g + delta))
    b = max(0, min(255, b + delta))
    return f"#{r:02x}{g:02x}{b:02x}"


def _section_label(parent, text: str) -> tk.Label:
    """Small uppercase section header for the dark sidebar."""
    return tk.Label(parent, text=text.upper(),
                    bg=P["sidebar"], fg=P["muted"],
                    font=FONT_XS, anchor="w",
                    padx=16, pady=0)


def _divider(parent) -> tk.Frame:
    return tk.Frame(parent, bg=P["sep"], height=1)


# ── Inline cell editor ─────────────────────────────────────────────────────────
class EditableCell(tk.Entry):
    def __init__(self, tree, item, col_idx, on_commit=None, on_before_commit=None, **kw):
        super().__init__(tree, **kw)
        self.tree, self.item, self.col_idx = tree, item, col_idx
        self._on_commit = on_commit
        self._on_before_commit = on_before_commit
        val = tree.item(item)["values"][col_idx]
        self.insert(0, str(val))
        self.select_range(0, tk.END)
        self.focus()
        self.bind("<Return>",   self._commit)
        self.bind("<Tab>",      self._commit)
        self.bind("<Escape>",   lambda _: self.destroy())
        self.bind("<FocusOut>", self._commit)

    def _commit(self, _=None):
        try:
            v = float(self.get().replace(",", "."))
        except ValueError:
            self.destroy()
            return
        if self._on_before_commit:
            self._on_before_commit()
        vals = list(self.tree.item(self.item)["values"])
        vals[self.col_idx] = v
        self.tree.item(self.item, values=vals)
        if self._on_commit:
            self._on_commit()
        self.destroy()


# ── Input row widget (entry + custom unit picker) ─────────────────────────────
class UnitEntry(tk.Frame):
    def __init__(self, parent, units: list[str], default_unit: str,
                 entry_width=12, fixed_unit=False, **kw):
        super().__init__(parent, bg=P["header2"], bd=0, **kw)
        self.unit_var = tk.StringVar(value=default_unit)
        self._units   = units

        self.entry = tk.Entry(
            self, bg=P["header2"], fg=P["text_inv"],
            relief="flat", bd=0, font=FONT, width=entry_width,
            insertbackground=P["text_inv"],
            selectbackground=P["accent"], selectforeground="#ffffff",
        )
        self.entry.pack(side=tk.LEFT, padx=(8, 0), pady=5)

        tk.Frame(self, bg=P["sep"], width=1).pack(
            side=tk.LEFT, fill=tk.Y, pady=5)

        if fixed_unit:
            tk.Label(self, text=default_unit,
                     bg=P["header2"], fg=P["muted"],
                     font=FONT, padx=10).pack(side=tk.LEFT)
        else:
            # ── Custom dropdown: button shows active unit, click → tk.Menu ──
            pick = tk.Frame(self, bg=P["header2"], cursor="hand2")
            pick.pack(side=tk.LEFT, fill=tk.Y)
            pick.bind("<Button-1>", lambda _: self._show_menu())

            self._unit_lbl = tk.Label(
                pick, textvariable=self.unit_var,
                bg=P["header2"], fg=P["text_inv"],
                font=FONT_B, padx=4, pady=0, cursor="hand2",
            )
            self._unit_lbl.pack(side=tk.LEFT, pady=5)
            self._unit_lbl.bind("<Button-1>", lambda _: self._show_menu())

            # "v" in a smaller, muted font works reliably on all platforms
            tk.Label(pick, text="v", bg=P["header2"], fg=P["muted"],
                     font=FONT_XS, padx=0).pack(
                side=tk.LEFT, padx=(0, 6), pady=5)

        self.entry.bind("<FocusIn>",  lambda _: self._highlight(True))
        self.entry.bind("<FocusOut>", lambda _: self._highlight(False))

    def _show_menu(self):
        m = tk.Menu(self, tearoff=0,
                    bg=P["header2"], fg=P["text_inv"],
                    activebackground=P["accent"],
                    activeforeground="#ffffff",
                    relief="flat", bd=1,
                    activeborderwidth=0, font=FONT)
        for u in self._units:
            m.add_command(
                label=f"  {u}  ",
                command=lambda v=u: self.unit_var.set(v),
            )
        lbl = self._unit_lbl
        m.post(lbl.winfo_rootx(),
               lbl.winfo_rooty() + lbl.winfo_height() + 2)

    def _highlight(self, on: bool):
        # Color the wrapper frame (master) — it provides the visible border
        try:
            self.master.configure(bg=P["accent"] if on else P["sep"])
        except tk.TclError:
            pass

    def get(self) -> str:        return self.entry.get()
    def unit(self) -> str:       return self.unit_var.get()
    def delete(self, *a):        self.entry.delete(*a)
    def focus(self):             self.entry.focus()
    def bind_entry(self, s, f):  self.entry.bind(s, f)


# ── Main application ───────────────────────────────────────────────────────────
class BodeTool:
    def __init__(self, root: tk.Tk, initial_file: str | None = None):
        self.root = root
        self.root.title("Bode Diagramm Tool")
        self.root.geometry("1340x800")
        self.root.minsize(980, 660)
        self.root.configure(bg=P["bg"])
        # View-toggle flags — created before menu/plot so both can bind to them
        self.opt_markers = tk.BooleanVar(value=True)
        self.opt_grid    = tk.BooleanVar(value=True)
        self.opt_dots    = tk.BooleanVar(value=True)
        self._dirty = False
        self._syncing_xlim = False
        self._xlim_cids: list = []
        self._undo_stack: list = []
        self._redo_stack: list = []
        self._configure_ttk()
        self._build_menubar()
        self._build_ui()
        self._init_plot()
        self._bind_shortcuts()
        self.project_var.trace_add("write", lambda *_: self._set_dirty())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        if initial_file and Path(initial_file).is_file():
            self.root.after(150, lambda: self._do_import_csv(initial_file))

    # ── Menu bar ──────────────────────────────────────────────────────────────
    def _build_menubar(self):
        # All menu callbacks are deferred with after(5) so the menu fully
        # closes before any canvas redraw happens — prevents header flicker.
        def d(fn):
            return lambda: self.root.after(5, fn)

        MK = dict(
            bg=P["sidebar"], fg=P["text_inv"],
            activebackground=P["accent"], activeforeground="#ffffff",
            relief="flat", bd=0, font=FONT, activeborderwidth=0,
        )
        bar = tk.Menu(
            self.root,
            bg=P["header"], fg=P["text_inv"],
            activebackground=P["accent_dk"], activeforeground="#ffffff",
            relief="flat", bd=0, font=FONT,
        )
        self.root.configure(menu=bar)

        # ── Datei ─────────────────────────────────────────────────────
        m_file = tk.Menu(bar, tearoff=0, **MK)
        bar.add_cascade(label="  Datei  ", menu=m_file)

        m_file.add_command(label="  Neu",
                           command=d(self._new_project), accelerator="Strg+N")
        m_file.add_separator()
        m_file.add_command(label="  CSV importieren …",
                           command=d(self._import_csv), accelerator="Strg+O")
        self._m_recent = tk.Menu(m_file, tearoff=0, **MK)
        m_file.add_cascade(label="  Zuletzt geöffnet", menu=self._m_recent)
        self._rebuild_recent_menu()
        m_file.add_command(label="  CSV exportieren …",
                           command=d(self._export_csv), accelerator="Strg+S")
        m_file.add_separator()

        m_save = tk.Menu(m_file, tearoff=0, **MK)
        m_file.add_cascade(label="  Plot speichern als …", menu=m_save)
        m_save.add_command(label="  PNG-Bild  (.png)",
                           command=d(lambda: self._save_plot("png")))
        m_save.add_command(label="  PDF-Dokument  (.pdf)",
                           command=d(lambda: self._save_plot("pdf")))
        m_save.add_command(label="  SVG-Vektorgrafik  (.svg)",
                           command=d(lambda: self._save_plot("svg")))

        m_file.add_separator()
        m_file.add_command(label="  Beenden",
                           command=self.root.quit, accelerator="Alt+F4")

        # ── Bearbeiten ─────────────────────────────────────────────────
        m_edit = tk.Menu(bar, tearoff=0, **MK)
        self._m_edit = m_edit
        bar.add_cascade(label="  Bearbeiten  ", menu=m_edit)

        m_edit.add_command(label="  Rückgängig",
                           command=d(self._undo), accelerator="Strg+Z",
                           state="disabled")
        m_edit.add_command(label="  Wiederherstellen",
                           command=d(self._redo), accelerator="Strg+Y",
                           state="disabled")
        m_edit.add_separator()
        m_edit.add_command(label="  Zeile löschen",
                           command=d(self._delete_selected), accelerator="Entf")
        m_edit.add_command(label="  Alle Zeilen löschen",
                           command=d(self._clear_all))
        m_edit.add_separator()
        m_edit.add_command(label="  Diagramm aktualisieren",
                           command=d(self._plot_bode), accelerator="F5")
        m_edit.add_separator()
        m_edit.add_command(label="  Alle auswählen",
                           command=d(self._select_all), accelerator="Strg+A")
        m_edit.add_separator()
        m_edit.add_command(label="  Nach Frequenz sortieren",
                           command=d(lambda: self._sort("freq")))
        m_edit.add_command(label="  Nach Amplitude sortieren",
                           command=d(lambda: self._sort("amplitude")))
        m_edit.add_command(label="  Nach Phase sortieren",
                           command=d(lambda: self._sort("phase")))

        # ── Ansicht ────────────────────────────────────────────────────
        m_view = tk.Menu(bar, tearoff=0, **MK)
        bar.add_cascade(label="  Ansicht  ", menu=m_view)

        m_view.add_checkbutton(
            label="  −3 dB / −45° Markierungen",
            variable=self.opt_markers, command=d(self._plot_bode),
            selectcolor=P["accent"])
        m_view.add_checkbutton(
            label="  Gitterlinien",
            variable=self.opt_grid, command=d(self._toggle_grid),
            selectcolor=P["accent"])
        m_view.add_checkbutton(
            label="  Datenpunkte markieren",
            variable=self.opt_dots, command=d(self._plot_bode),
            selectcolor=P["accent"])

        # ── Hilfe ──────────────────────────────────────────────────────
        m_help = tk.Menu(bar, tearoff=0, **MK)
        bar.add_cascade(label="  Hilfe  ", menu=m_help)

        m_help.add_command(label="  CSV-Format Anleitung",
                           command=d(self._show_csv_help), accelerator="F1")
        m_help.add_separator()
        m_help.add_command(label="  Über Bode Diagramm Tool …",
                           command=d(self._show_about))

    # ── Unsaved-changes guard ──────────────────────────────────────────────────
    def _set_dirty(self):
        self._dirty = True

    def _data_changed(self):
        """Called after every data mutation; marks dirty and auto-refreshes the plot."""
        self._set_dirty()
        if self.tree.get_children():
            self._plot_bode(silent=True)
        else:
            self._init_plot()
            self.canvas.draw_idle()

    # ── Undo / Redo ───────────────────────────────────────────────────────────
    _MAX_UNDO = 50

    def _snapshot(self):
        return tuple(
            tuple(self.tree.item(i)["values"])
            for i in self.tree.get_children()
        )

    def _save_undo_state(self):
        state = self._snapshot()
        if self._undo_stack and self._undo_stack[-1] == state:
            return
        self._undo_stack.append(state)
        if len(self._undo_stack) > self._MAX_UNDO:
            del self._undo_stack[0]
        self._redo_stack.clear()
        self._update_undo_menu()

    def _undo(self):
        if not self._undo_stack:
            return
        self._redo_stack.append(self._snapshot())
        self._restore_state(self._undo_stack.pop())
        self._update_undo_menu()

    def _redo(self):
        if not self._redo_stack:
            return
        self._undo_stack.append(self._snapshot())
        self._restore_state(self._redo_stack.pop())
        self._update_undo_menu()

    def _restore_state(self, state):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for idx, row in enumerate(state):
            self.tree.insert("", tk.END, values=row,
                             tags=("odd" if idx % 2 else "even",))
        self._set_dirty()
        self._update_status()
        if state:
            self._plot_bode(silent=True)
        else:
            self._init_plot()
            self.canvas.draw_idle()

    def _update_undo_menu(self):
        self._m_edit.entryconfig(
            "  Rückgängig",
            state="normal" if self._undo_stack else "disabled")
        self._m_edit.entryconfig(
            "  Wiederherstellen",
            state="normal" if self._redo_stack else "disabled")

    def _on_close(self):
        if self._dirty and self.tree.get_children():
            if not self._dlg(
                "Beenden",
                "Es gibt ungespeicherte Daten.\n"
                "Vor dem Beenden als CSV speichern?",
                "confirm",
            ):
                self.root.destroy()
            else:
                self._export_csv()
        else:
            self.root.destroy()

    # ── Keyboard shortcuts ─────────────────────────────────────────────────────
    def _bind_shortcuts(self):
        for seq, fn in [
            ("<Control-n>",       self._new_project),
            ("<Control-N>",       self._new_project),
            ("<Control-o>",       self._import_csv),
            ("<Control-O>",       self._import_csv),
            ("<Control-s>",       self._export_csv),
            ("<Control-S>",       self._export_csv),
            ("<Control-a>",       self._select_all),
            ("<Control-A>",       self._select_all),
            ("<Control-z>",       self._undo),
            ("<Control-Z>",       self._undo),
            ("<Control-y>",       self._redo),
            ("<Control-Y>",       self._redo),
            ("<Control-Shift-Z>", self._redo),
            ("<F5>",              self._plot_bode),
            ("<F1>",              self._show_csv_help),
        ]:
            self.root.bind_all(seq, lambda _, f=fn: f())

    # ── TTK styles ─────────────────────────────────────────────────────────────
    def _configure_ttk(self):
        s = ttk.Style()
        for theme in ("clam", "alt", "default"):
            if theme in s.theme_names():
                s.theme_use(theme)
                break

        # Treeview
        s.configure("Bode.Treeview",
                    background=P["row_b"],
                    fieldbackground=P["row_b"],
                    foreground=P["text"],
                    rowheight=26,
                    font=FONT,
                    borderwidth=0,
                    relief="flat")
        s.configure("Bode.Treeview.Heading",
                    background=P["bg"],
                    foreground=P["text"],
                    font=FONT_B,
                    relief="flat",
                    borderwidth=0,
                    padding=(4, 6))
        s.map("Bode.Treeview",
              background=[("selected", P["accent_lt"])],
              foreground=[("selected", P["accent_dk"])])
        s.map("Bode.Treeview.Heading",
              background=[("active", P["border"])])

        # Combobox inside UnitEntry
        s.configure("TCombobox", relief="flat", borderwidth=0,
                    selectbackground=P["accent_lt"],
                    selectforeground=P["accent_dk"])

        # Scrollbar
        s.configure("Vertical.TScrollbar",
                    troughcolor=P["bg"],
                    background=P["border"],
                    relief="flat", borderwidth=0)

    # ── UI scaffold ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Header bar ──────────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg=P["header"], height=56)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)

        try:
            _logo = _ITk.PhotoImage(
                Image.open(BytesIO(base64.b64decode(_ICON_PNG))).resize(
                    (32, 32), Image.LANCZOS))
            self._hdr_logo = _logo  # keep reference so GC doesn't blank it
            tk.Label(hdr, image=_logo, bg=P["header"]).pack(
                side=tk.LEFT, padx=(16, 6))
        except Exception:
            pass
        tk.Label(hdr, text="Bode Diagramm Tool",
                 bg=P["header"], fg=P["text_inv"],
                 font=(_SANS, 14, "bold")).pack(side=tk.LEFT, padx=(0, 28))

        tk.Label(hdr, text="Projektname:",
                 bg=P["header"], fg=P["muted"],
                 font=FONT_B).pack(side=tk.LEFT, padx=(0, 6))

        self.project_var = tk.StringVar()
        proj_e = tk.Entry(hdr, textvariable=self.project_var,
                          bg=P["header2"], fg=P["text_inv"],
                          insertbackground=P["text_inv"],
                          relief="flat", bd=0, font=(_SANS, 11),
                          width=32)
        proj_e.pack(side=tk.LEFT, ipady=6, padx=(0, 4))
        proj_e.bind("<KeyRelease>", lambda _: self._sync_title())

        # ── Two-column layout ────────────────────────────────────────────────
        body = tk.Frame(self.root, bg=P["bg"])
        body.pack(fill=tk.BOTH, expand=True)

        # Left sidebar (dark navy)
        self.sidebar = tk.Frame(body, bg=P["sidebar"], width=320)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Thin border line between sidebar and content
        tk.Frame(body, bg=P["border"], width=1).pack(side=tk.LEFT, fill=tk.Y)

        # Right content area
        right = tk.Frame(body, bg=P["bg"])
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_sidebar(self.sidebar)
        self._build_plot_area(right)

        # ── Status bar ───────────────────────────────────────────────────────
        sb = tk.Frame(self.root, bg=P["header"], height=26)
        sb.pack(fill=tk.X, side=tk.BOTTOM)
        sb.pack_propagate(False)
        self.status_var = tk.StringVar(value="Keine Daten")
        tk.Label(sb, textvariable=self.status_var,
                 bg=P["header"], fg=P["muted"],
                 font=FONT_SM, anchor="w").pack(side=tk.LEFT, padx=14)

    def _sync_title(self):
        name = self.project_var.get().strip()
        self.root.title(f"Bode Diagramm Tool — {name}" if name
                        else "Bode Diagramm Tool")
        self._refresh_suptitle()

    def _update_status(self):
        n = len(self.tree.get_children())
        self.status_var.set(
            f"  {n} Datenpunkt{'e' if n != 1 else ''}  •  "
            "Doppelklick zum Bearbeiten  •  Entf zum Löschen"
        )

    # ── Sidebar ─────────────────────────────────────────────────────────────
    def _build_sidebar(self, parent):
        # Pack BOTTOM items first (first packed = very bottom).
        # This lets the treeview (packed TOP + expand) fill the remaining middle.

        # ── CTA buttons — anchored to bottom ──────────────────────────
        cta = tk.Frame(parent, bg=P["sidebar"], padx=12, pady=10)
        cta.pack(side=tk.BOTTOM, fill=tk.X)
        _btn(cta, "Plot speichern",
             self._save_plot, P["accent"],
             icon=_icon("save")).pack(fill=tk.X, ipady=6)

        # ── Section: Datei ─────────────────────────────────────────────
        _divider(parent).pack(side=tk.BOTTOM, fill=tk.X)
        fa = tk.Frame(parent, bg=P["sidebar"], padx=12)
        fa.pack(side=tk.BOTTOM, fill=tk.X)
        fa.columnconfigure(0, weight=1)
        fa.columnconfigure(1, weight=1)
        for i, (lbl, cmd, ico) in enumerate([
            ("CSV importieren", self._import_csv,   "import"),
            ("CSV exportieren", self._export_csv,   "export"),
            ("?  CSV-Format",   self._show_csv_help, None),
        ]):
            r, c = divmod(i, 2)
            _btn(fa, lbl, cmd, "#2e4470", P["text_inv"],
                 icon=_icon(ico) if ico else None).grid(
                row=r, column=c, sticky="ew",
                padx=(0, 4) if c == 0 else (4, 0), pady=(0, 5))
        _section_label(parent, "Datei").pack(
            side=tk.BOTTOM, fill=tk.X, pady=(8, 4))

        # ── Section: Tabelle ───────────────────────────────────────────
        _divider(parent).pack(side=tk.BOTTOM, fill=tk.X)
        ra = tk.Frame(parent, bg=P["sidebar"], padx=12)
        ra.pack(side=tk.BOTTOM, fill=tk.X)
        ra.columnconfigure(0, weight=1)
        ra.columnconfigure(1, weight=1)
        _btn(ra, "Zeile löschen", self._delete_selected,
             "#2e4470", P["text_inv"], icon=_icon("trash")).grid(
            row=0, column=0, sticky="ew", padx=(0, 4))
        _btn(ra, "✕  Alle löschen", self._clear_all,
             "#2e4470", P["text_inv"]).grid(
            row=0, column=1, sticky="ew", padx=(4, 0))
        _section_label(parent, "Tabelle").pack(
            side=tk.BOTTOM, fill=tk.X, pady=(8, 4))

        # ── Section: Zeile einfügen ────────────────────────────────────
        _divider(parent).pack(side=tk.BOTTOM, fill=tk.X)
        ef = tk.Frame(parent, bg=P["sidebar"], padx=12)
        ef.pack(side=tk.BOTTOM, fill=tk.X)
        ef.columnconfigure(1, weight=1)

        self.ue_freq  = self._input_row(ef, "Frequenz",
                                         list(FREQ_UNITS), "Hz",  row=0)
        self.ue_amp   = self._input_row(ef, "Amplitude",
                                         list(AMP_UNITS),  "dB",  row=1)
        self.ue_phase = self._input_row(ef, "Phase",
                                         ["°"],             "°",   row=2,
                                         fixed_unit=True)
        for ue in (self.ue_freq, self.ue_amp, self.ue_phase):
            ue.bind_entry("<Return>", self._on_entry_return)
        _btn(ef, "+ Hinzufügen", self._add_row,
             P["accent"]).grid(row=3, column=0, columnspan=2,
                               sticky="ew", pady=(8, 0))

        _section_label(parent, "Zeile einfügen").pack(
            side=tk.BOTTOM, fill=tk.X, pady=(8, 4))
        _divider(parent).pack(side=tk.BOTTOM, fill=tk.X, pady=(4, 0))

        # ── Section: Messdaten (TOP) — treeview fills the middle ───────
        _section_label(parent, "Messdaten").pack(fill=tk.X, pady=(14, 4))

        tree_wrap = tk.Frame(parent, bg=P["sidebar"], padx=12)
        tree_wrap.pack(fill=tk.BOTH, expand=True)

        tree_card = tk.Frame(tree_wrap, bg=P["row_b"],
                             highlightbackground=P["border"],
                             highlightthickness=1)
        tree_card.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_card, style="Bode.Treeview",
                                  columns=COLUMNS, show="headings",
                                  selectmode="extended")
        widths = (88, 95, 80)
        for col, lbl, w in zip(COLUMNS, COL_LABELS, widths):
            self.tree.heading(col, text=lbl,
                              command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, anchor="center", stretch=True)
        self.tree.tag_configure("odd",  background=P["row_a"])
        self.tree.tag_configure("even", background=P["row_b"])

        vsb = ttk.Scrollbar(tree_card, orient=tk.VERTICAL,
                             command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Delete>",   lambda _: self._delete_selected())

    def _input_row(self, parent, label: str, units: list, default: str,
                   row: int, fixed_unit=False) -> UnitEntry:
        tk.Label(parent, text=label, bg=P["sidebar"], fg=P["text_inv"],
                 font=FONT, anchor="w").grid(
            row=row, column=0, sticky="w", pady=(0, 6))

        # Wrapper frame provides a reliable 1px border on all platforms.
        # On Windows, highlightthickness on a Frame is only visible when
        # focused, so we use the wrapper's bg as the persistent border color.
        bdr = tk.Frame(parent, bg=P["sep"], padx=1, pady=1)
        bdr.grid(row=row, column=1, sticky="ew", padx=(6, 0), pady=(0, 6))
        bdr.columnconfigure(0, weight=1)
        ue = UnitEntry(bdr, units, default, entry_width=11, fixed_unit=fixed_unit)
        ue.pack(fill=tk.X)
        parent.columnconfigure(1, weight=1)
        return ue

    # ── Plot area ────────────────────────────────────────────────────────────
    def _build_plot_area(self, parent):
        self.fig = Figure(figsize=(9, 6.5), dpi=100)
        self.fig.patch.set_facecolor(P["bg"])
        self.ax_mag   = self.fig.add_subplot(2, 1, 1)
        self.ax_phase = self.fig.add_subplot(2, 1, 2)
        self.fig.subplots_adjust(
            hspace=0.42, top=0.90, bottom=0.09, left=0.09, right=0.97)

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True,
                                          padx=0, pady=0)

        tb_frame = tk.Frame(parent, bg=P["bg"])
        tb_frame.pack(fill=tk.X)
        toolbar = NavigationToolbar2Tk(self.canvas, tb_frame)
        toolbar.update()
        # Apply theme colors to toolbar and all its children
        self._style_widget(toolbar, P["bg"], P["text"])

    @staticmethod
    def _style_widget(widget, bg: str, fg: str):
        """Recursively apply bg/fg to a widget tree (best-effort)."""
        try:
            widget.configure(bg=bg)
        except tk.TclError:
            pass
        for child in widget.winfo_children():
            try:
                child.configure(
                    bg=bg, fg=fg,
                    activebackground=_shade(bg, -15),
                    activeforeground=fg,
                    relief="flat", bd=0,
                    highlightthickness=0,
                )
            except tk.TclError:
                pass
            BodeTool._style_widget(child, bg, fg)

    def _init_plot(self):
        for ax, title, ylabel in (
            (self.ax_mag,   "Amplitudengang", "Amplitude (dB)"),
            (self.ax_phase, "Phasengang",     "Phase (°)"),
        ):
            ax.clear()
            ax.set_facecolor("#fafcff")
            ax.set_xscale("log")
            ax.set_title(title, fontsize=10, fontweight="bold",
                         color=P["text"], pad=8)
            ax.set_ylabel(ylabel, fontsize=9, color=P["text"])
            ax.tick_params(colors=P["text"], labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor(P["border"])
            ax.grid(True, which="major", color=P["border"],
                    linestyle="-", linewidth=0.8)
            ax.grid(True, which="minor", color=P["border"],
                    linestyle=":", linewidth=0.5, alpha=0.6)
        self.ax_phase.set_xlabel("Frequenz (Hz)", fontsize=9, color=P["text"])
        self._refresh_suptitle()
        self._connect_xlim_sync()

    def _connect_xlim_sync(self):
        """Keep both plots' frequency axis in sync during zoom/pan."""
        for ax, cid in self._xlim_cids:
            try:
                ax.callbacks.disconnect(cid)
            except Exception:
                pass

        def _on_mag_xlim(ax):
            if not self._syncing_xlim:
                self._syncing_xlim = True
                self.ax_phase.set_xlim(ax.get_xlim())
                self._syncing_xlim = False

        def _on_phase_xlim(ax):
            if not self._syncing_xlim:
                self._syncing_xlim = True
                self.ax_mag.set_xlim(ax.get_xlim())
                self._syncing_xlim = False

        cid1 = self.ax_mag.callbacks.connect('xlim_changed', _on_mag_xlim)
        cid2 = self.ax_phase.callbacks.connect('xlim_changed', _on_phase_xlim)
        self._xlim_cids = [(self.ax_mag, cid1), (self.ax_phase, cid2)]

    def _refresh_suptitle(self):
        name = self.project_var.get().strip()
        title = f"Bode Diagramm  —  {name}" if name else "Bode Diagramm"
        self.fig.suptitle(title, fontsize=13, fontweight="bold",
                          color=P["text"], y=0.97)
        self.canvas.draw_idle()

    # ── Styled dialog (replaces messagebox) ──────────────────────────────────
    def _dlg(self, title: str, msg: str, kind: str = "info") -> bool:
        """Modal dialog matching the app theme.
        kind: 'info' | 'error' | 'warn' | 'confirm'
        Returns True when user clicks OK / Ja."""
        accent = {"info":  P["accent"], "error": P["danger"],
                  "warn":  P["warning"], "confirm": P["warning"]}.get(kind, P["accent"])
        icon   = {"info": "i", "error": "✕", "warn": "!", "confirm": "?"}.get(kind, "i")

        result = [False]
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=P["bg"])
        win.resizable(False, False)
        win.grab_set()
        win.focus_set()

        # Coloured accent bar at top
        tk.Frame(win, bg=accent, height=5).pack(fill=tk.X)

        # Body
        body = tk.Frame(win, bg=P["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=(18, 10))

        # Icon pill + title
        top = tk.Frame(body, bg=P["bg"])
        top.pack(fill=tk.X, pady=(0, 10))
        tk.Label(top, text=icon, bg=accent, fg="#ffffff",
                 font=FONT_B, padx=7, pady=2).pack(side=tk.LEFT)
        tk.Label(top, text=f"  {title}", bg=P["bg"], fg=P["text"],
                 font=FONT_B).pack(side=tk.LEFT)

        # Message text
        tk.Label(body, text=msg, bg=P["bg"], fg=P["text"],
                 font=FONT, wraplength=320, justify="left").pack(anchor="w")

        # Buttons
        br = tk.Frame(win, bg=P["bg"])
        br.pack(fill=tk.X, padx=24, pady=(8, 20))
        if kind == "confirm":
            def _yes():
                result[0] = True
                win.destroy()
            _btn(br, "Ja",   _yes,        P["accent"], padx=14).pack(side=tk.RIGHT, padx=(6, 0), ipady=4)
            _btn(br, "Nein", win.destroy, "#2e4470", P["text_inv"], padx=14).pack(side=tk.RIGHT, ipady=4)
        else:
            _btn(br, "OK", win.destroy, P["accent"], padx=14).pack(side=tk.RIGHT, ipady=4)

        # Centre on parent
        win.update_idletasks()
        pw, ph = self.root.winfo_width(), self.root.winfo_height()
        px, py = self.root.winfo_x(),     self.root.winfo_y()
        ww, wh = win.winfo_reqwidth(),    win.winfo_reqheight()
        win.geometry(f"+{px + (pw - ww)//2}+{py + (ph - wh)//2}")

        win.wait_window()
        return result[0]

    # ── Table helpers ────────────────────────────────────────────────────────
    def _retag(self):
        for i, item in enumerate(self.tree.get_children()):
            self.tree.item(item, tags=("odd" if i % 2 else "even",))

    def _on_entry_return(self, event):
        ues = [self.ue_freq, self.ue_amp, self.ue_phase]
        widgets = [ue.entry for ue in ues]
        idx = widgets.index(event.widget)
        if idx < len(ues) - 1:
            ues[idx + 1].focus()
        else:
            self._add_row()

    def _parse_freq(self, raw: str) -> float:
        val = float(raw.strip().replace(",", "."))
        val *= FREQ_UNITS[self.ue_freq.unit()]
        if val <= 0:
            raise ValueError("Frequenz muss > 0 sein.")
        return val

    def _parse_amp(self, raw: str) -> float:
        val  = float(raw.strip().replace(",", "."))
        unit = self.ue_amp.unit()
        if unit == "dB":
            return val
        return v_to_db(val * AMP_UNITS[unit])

    def _add_row(self):
        try:
            freq  = self._parse_freq(self.ue_freq.get())
            amp   = self._parse_amp(self.ue_amp.get())
            phase = float(self.ue_phase.get().strip().replace(",", "."))
        except ValueError as exc:
            self._dlg("Eingabefehler",
                      str(exc) or "Bitte gültige Zahlen eingeben.", "error")
            return
        self._save_undo_state()
        n = len(self.tree.get_children())
        tag = "odd" if n % 2 else "even"
        self.tree.insert("", tk.END,
                         values=(round(freq, 6), round(amp, 4), round(phase, 4)),
                         tags=(tag,))
        for ue in (self.ue_freq, self.ue_amp, self.ue_phase):
            ue.delete(0, tk.END)
        self.ue_freq.focus()
        self._data_changed()
        self._update_status()

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            self._dlg("Hinweis", "Keine Zeile ausgewählt.", "info")
            return
        self._save_undo_state()
        for item in sel:
            self.tree.delete(item)
        self._retag()
        self._data_changed()
        self._update_status()

    def _clear_all(self):
        if self.tree.get_children() and \
                self._dlg("Bestätigen", "Alle Zeilen löschen?", "confirm"):
            self._save_undo_state()
            for item in self.tree.get_children():
                self.tree.delete(item)
            self._data_changed()
            self._update_status()

    def _on_double_click(self, event):
        row = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not row or not col:
            return
        col_idx = int(col.lstrip("#")) - 1
        x, y, w, h = self.tree.bbox(row, col)
        EditableCell(self.tree, row, col_idx,
                     on_before_commit=self._save_undo_state,
                     on_commit=self._data_changed,
                     font=FONT, bg=P["accent_lt"],
                     fg=P["text"]).place(x=x, y=y, width=w, height=h)

    def _sort(self, col):
        self._save_undo_state()
        col_idx = COLUMNS.index(col)
        data = [(float(self.tree.item(k)["values"][col_idx]), k)
                for k in self.tree.get_children()]
        data.sort()
        for i, (_, k) in enumerate(data):
            self.tree.move(k, "", i)
        self._retag()

    def _get_sorted_data(self):
        rows = []
        for item in self.tree.get_children():
            v = self.tree.item(item)["values"]
            rows.append((float(v[0]), float(v[1]), float(v[2])))
        return sorted(rows, key=lambda r: r[0])

    # ── Recent files ──────────────────────────────────────────────────────────
    def _load_recent(self) -> list:
        try:
            data = json.loads(_RECENT_PATH.read_text(encoding="utf-8"))
            return [p for p in data if isinstance(p, str)]
        except Exception:
            return []

    def _save_recent(self, path: str):
        recent = [p for p in self._load_recent() if p != path]
        recent.insert(0, path)
        try:
            _RECENT_PATH.write_text(
                json.dumps(recent[:_RECENT_MAX], ensure_ascii=False, indent=2),
                encoding="utf-8")
        except Exception:
            pass
        self._rebuild_recent_menu()

    def _rebuild_recent_menu(self):
        self._m_recent.delete(0, tk.END)
        recent = self._load_recent()
        if not recent:
            self._m_recent.add_command(label="  (keine)", state="disabled")
            return
        for path in recent:
            name = Path(path).name
            self._m_recent.add_command(
                label=f"  {name}",
                command=lambda p=path: self.root.after(5, lambda p=p: self._open_recent(p)))
        self._m_recent.add_separator()
        self._m_recent.add_command(
            label="  Liste leeren",
            command=lambda: self.root.after(5, self._clear_recent))

    def _open_recent(self, path: str):
        if not Path(path).exists():
            self._dlg("Datei nicht gefunden",
                      f"Die Datei wurde nicht gefunden und wird aus der Liste entfernt:\n{path}",
                      "warn")
            recent = [p for p in self._load_recent() if p != path]
            try:
                _RECENT_PATH.write_text(
                    json.dumps(recent, ensure_ascii=False, indent=2),
                    encoding="utf-8")
            except Exception:
                pass
            self._rebuild_recent_menu()
            return
        self._do_import_csv(path)

    def _clear_recent(self):
        try:
            _RECENT_PATH.write_text("[]", encoding="utf-8")
        except Exception:
            pass
        self._rebuild_recent_menu()

    # ── CSV ──────────────────────────────────────────────────────────────────
    def _sniff(self, path):
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            sample = f.read(4096)
        delim   = ";" if sample.count(";") >= sample.count(",") else ","
        decimal = "," if delim == ";" else "."
        return delim, decimal

    def _import_csv(self):
        path = filedialog.askopenfilename(
            title="CSV Datei öffnen",
            filetypes=[("CSV Dateien", "*.csv"), ("Alle Dateien", "*.*")])
        if not path:
            return
        self._do_import_csv(path)

    def _do_import_csv(self, path: str):
        self._save_undo_state()
        delim, decimal = self._sniff(path)

        def parse(s):
            return float(s.strip().replace(decimal, "."))

        count = errors = 0
        try:
            with open(path, encoding="utf-8-sig",
                      errors="replace", newline="") as f:
                reader = csv.reader(f, delimiter=delim)
                freq_idx = amp_idx = phase_idx = None
                header_done = False

                for raw in reader:
                    if not any(c.strip() for c in raw):
                        continue
                    first = raw[0].strip()
                    if first.startswith("#"):
                        if "projekt" in first.lower() and ":" in first:
                            self.project_var.set(
                                first.split(":", 1)[1].strip())
                            self._sync_title()
                        continue

                    if not header_done:
                        header_done = True
                        hl = [c.lower().strip() for c in raw]
                        for i, h in enumerate(hl):
                            if any(k in h for k in ("freq","hz","f(")):
                                freq_idx = i
                            elif any(k in h for k in ("amp","db","gain",
                                                       "mag","betr")):
                                amp_idx = i
                            elif any(k in h for k in ("phase","pha","grad",
                                                       "deg","winkel")):
                                phase_idx = i
                        if None in (freq_idx, amp_idx, phase_idx):
                            freq_idx, amp_idx, phase_idx = 0, 1, 2
                            try:
                                n = len(self.tree.get_children())
                                self.tree.insert(
                                    "", tk.END,
                                    values=(parse(raw[0]),
                                            parse(raw[1]),
                                            parse(raw[2])),
                                    tags=("odd" if n % 2 else "even",))
                                count += 1
                            except (ValueError, IndexError):
                                pass
                        continue

                    try:
                        n = len(self.tree.get_children())
                        self.tree.insert(
                            "", tk.END,
                            values=(parse(raw[freq_idx]),
                                    parse(raw[amp_idx]),
                                    parse(raw[phase_idx])),
                            tags=("odd" if n % 2 else "even",))
                        count += 1
                    except (ValueError, IndexError):
                        errors += 1

        except Exception as exc:
            self._dlg("Importfehler", str(exc), "error")
            return

        self._save_recent(path)
        self._update_status()
        self._data_changed()
        msg = f"{count} Zeilen importiert."
        if errors:
            msg += f"\n{errors} Zeile(n) übersprungen."
        self._dlg("Import", msg, "info")

    def _export_csv(self):
        data = self._get_sorted_data()
        if not data:
            self._dlg("Hinweis", "Keine Daten vorhanden.", "info")
            return
        path = filedialog.asksaveasfilename(
            title="CSV speichern", defaultextension=".csv",
            filetypes=[("CSV Dateien", "*.csv"), ("Alle Dateien", "*.*")])
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, delimiter=";")
                proj = self.project_var.get().strip()
                if proj:
                    w.writerow([f"# Projekt: {proj}"])
                w.writerow(COL_LABELS)
                w.writerows(data)
            self._dirty = False
            self._dlg("Export", f"Gespeichert:\n{path}", "info")
        except Exception as exc:
            self._dlg("Exportfehler", str(exc), "error")

    def _show_csv_help(self):
        win = tk.Toplevel(self.root)
        win.title("CSV-Format Anleitung")
        win.geometry("600x580")
        win.configure(bg=P["sidebar"])
        win.resizable(True, True)

        # Header bar
        hdr = tk.Frame(win, bg=P["header"], height=52)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="CSV-Format Anleitung",
                 bg=P["header"], fg=P["text_inv"],
                 font=FONT_LG).pack(side=tk.LEFT, padx=18, pady=14)
        _divider(win).pack(fill=tk.X)

        # Text area
        card = tk.Frame(win, bg=P["sidebar"], padx=14, pady=10)
        card.pack(fill=tk.BOTH, expand=True)

        txt = tk.Text(card, wrap=tk.WORD, font=FONT_MONO,
                      bg=P["header2"], fg=P["text_inv"],
                      insertbackground=P["text_inv"],
                      padx=14, pady=12, relief="flat",
                      selectbackground=P["accent"],
                      selectforeground="#ffffff",
                      borderwidth=0)
        sb = ttk.Scrollbar(card, orient=tk.VERTICAL, command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        txt.insert("1.0", CSV_HELP)
        txt.config(state=tk.DISABLED)

        _divider(win).pack(fill=tk.X)
        foot = tk.Frame(win, bg=P["sidebar"])
        foot.pack(fill=tk.X, padx=18, pady=(10, 14))
        _btn(foot, "Schließen", win.destroy,
             P["accent"], padx=14).pack(side=tk.RIGHT, ipady=5)

    # ── Plotting ─────────────────────────────────────────────────────────────
    def _plot_bode(self, silent=False):
        data = self._get_sorted_data()
        if not data:
            if not silent:
                self._dlg("Warnung", "Keine Daten vorhanden.", "warn")
            return

        freqs  = np.array([d[0] for d in data])
        amps   = np.array([d[1] for d in data])
        phases = np.array([d[2] for d in data])

        self._init_plot()

        use_dots = self.opt_dots.get() and len(data) <= 80
        marker = "o" if use_dots else ""
        kw = dict(linewidth=2.2, marker=marker, markersize=5,
                  markerfacecolor="white", markeredgewidth=1.5,
                  solid_capstyle="round")

        self.ax_mag.semilogx(freqs, amps,   color=P["accent"],
                             label="Amplitude (dB)", **kw)
        self.ax_mag.set_ylabel("Amplitude (dB)", fontsize=9)
        self.ax_mag.legend(fontsize=8, framealpha=0.9)

        self.ax_phase.semilogx(freqs, phases, color="#e85d04",
                               label="Phase (°)", **kw)
        self.ax_phase.set_ylabel("Phase (°)", fontsize=9)
        self.ax_phase.set_xlabel("Frequenz (Hz)", fontsize=9)
        self.ax_phase.legend(fontsize=8, framealpha=0.9)

        if self.opt_markers.get():
            self._add_marker(self.ax_mag,   freqs, amps,   -3,  P["warning"], "−3 dB")
            self._add_marker(self.ax_phase, freqs, phases, -45, P["success"], "−45°")

        self.canvas.draw_idle()

    def _add_marker(self, ax, x, y, target, color, label):
        ax.axhline(target, color=color, linestyle="--",
                   linewidth=1.2, alpha=0.85, label=label)
        for i in range(len(y) - 1):
            y0, y1 = y[i], y[i + 1]
            if min(y0, y1) <= target <= max(y0, y1):
                t = (target - y0) / (y1 - y0)
                xc = np.exp(np.log(x[i]) + t * (np.log(x[i+1]) - np.log(x[i])))
                ax.axvline(xc, color=color, linestyle=":",
                           linewidth=1.0, alpha=0.75)
                ax.annotate(f" {xc:.3g} Hz",
                            xy=(xc, target),
                            xytext=(4, 5), textcoords="offset points",
                            fontsize=7.5, color=color, fontweight="bold")
                break
        ax.legend(fontsize=8, framealpha=0.9)

    def _save_plot(self, fmt: str | None = None):
        fmt_map = {
            "png": ("PNG-Bild",        "*.png"),
            "pdf": ("PDF-Dokument",    "*.pdf"),
            "svg": ("SVG-Vektorgrafik","*.svg"),
        }
        if fmt and fmt in fmt_map:
            lbl, ext = fmt_map[fmt]
            path = filedialog.asksaveasfilename(
                title=f"Plot als {fmt.upper()} speichern",
                defaultextension=f".{fmt}",
                filetypes=[(lbl, ext), ("Alle Dateien", "*.*")])
        else:
            path = filedialog.asksaveasfilename(
                title="Diagramm speichern", defaultextension=".png",
                filetypes=[("PNG-Bild", "*.png"),
                            ("PDF-Dokument", "*.pdf"),
                            ("SVG-Vektorgrafik", "*.svg")])
        if not path:
            return
        try:
            self.fig.savefig(path, dpi=200, bbox_inches="tight",
                             facecolor=P["bg"])
            self._dlg("Gespeichert", f"Diagramm gespeichert:\n{path}", "info")
        except Exception as exc:
            self._dlg("Fehler", str(exc), "error")


    # ── Extra actions (menu targets) ──────────────────────────────────────────
    def _new_project(self):
        if self.tree.get_children():
            if not self._dlg("Neu",
                    "Alle Daten verwerfen und neu beginnen?", "confirm"):
                return
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.project_var.set("")
        self._sync_title()
        self._init_plot()
        self._update_status()
        self._dirty = False

    def _select_all(self):
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def _toggle_grid(self):
        on = self.opt_grid.get()
        for ax in (self.ax_mag, self.ax_phase):
            ax.grid(on, which="major", color=P["border"],
                    linestyle="-", linewidth=0.8)
            ax.grid(on, which="minor", color=P["border"],
                    linestyle=":", linewidth=0.5, alpha=0.6)
        self.canvas.draw_idle()

    def _open_url(self, url: str):
        import webbrowser
        webbrowser.open(url)

    def _show_about(self):
        win = tk.Toplevel(self.root)
        win.title("Über Bode Diagramm Tool")
        win.geometry("380x290")
        win.configure(bg=P["sidebar"])
        win.resizable(False, False)

        # Full-width dark header
        hdr = tk.Frame(win, bg=P["header"], height=72)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        try:
            _alogo = _ITk.PhotoImage(
                Image.open(BytesIO(base64.b64decode(_ICON_PNG))).resize(
                    (28, 28), Image.LANCZOS))
            self._about_logo = _alogo
            inner = tk.Frame(hdr, bg=P["header"])
            inner.pack(expand=True)
            tk.Label(inner, image=_alogo, bg=P["header"]).pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(inner, text="Bode Diagramm Tool",
                     bg=P["header"], fg=P["text_inv"],
                     font=FONT_LG).pack(side=tk.LEFT)
        except Exception:
            tk.Label(hdr, text="Bode Diagramm Tool",
                     bg=P["header"], fg=P["text_inv"],
                     font=FONT_LG).pack(expand=True)
        _divider(win).pack(fill=tk.X)

        # Body
        body = tk.Frame(win, bg=P["sidebar"])
        body.pack(fill=tk.BOTH, expand=True, padx=22, pady=(16, 0))

        for text, col, fnt, bot_pad in [
            ("Visualisierung von Frequenzgängen",          P["text_inv"], FONT,    2),
            ("aus gemessenen Übertragungsverhalten.",       P["text_inv"], FONT,    12),
            ("Eingabe:  Frequenz  ·  Amplitude  ·  Phase",  P["muted"],   FONT_SM, 3),
            ("Export:   CSV  ·  PNG  ·  PDF  ·  SVG",       P["muted"],   FONT_SM, 12),
        ]:
            tk.Label(body, text=text, bg=P["sidebar"], fg=col,
                     font=fnt, anchor="w").pack(anchor="w", pady=(0, bot_pad))

        gh_url = "github.com/FelixLenz-Code/bode-diagramm-tool"
        gh_lbl = tk.Label(body, text=f">> {gh_url}",
                          bg=P["sidebar"], fg=P["accent"],
                          font=FONT_SM, anchor="w", cursor="hand2")
        gh_lbl.pack(anchor="w")
        gh_lbl.bind("<Button-1>", lambda _: self._open_url(
            "https://github.com/FelixLenz-Code/bode-diagramm-tool"))

        _divider(win).pack(fill=tk.X)
        foot = tk.Frame(win, bg=P["sidebar"])
        foot.pack(fill=tk.X, padx=22, pady=(10, 16))
        _btn(foot, "Schließen", win.destroy,
             P["accent"], padx=14).pack(side=tk.RIGHT, ipady=5)

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    try:
        _img = _ITk.PhotoImage(Image.open(BytesIO(base64.b64decode(_ICON_PNG))))
        root.iconphoto(True, _img)
    except Exception:
        pass
    _initial = sys.argv[1] if len(sys.argv) > 1 else None
    BodeTool(root, initial_file=_initial)
    root.mainloop()
