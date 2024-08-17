import geoip2.database
import src.tools.repositories as repositories

# ===================== IP获取地区 ===================== #

def get_country_for_ip(ip):
    with geoip2.database.Reader(repositories.GEOIP2_DB_PATH) as reader:
        try:
            return reader.country(ip).country.iso_code
        except geoip2.errors.AddressNotFoundError:
            pass
        except geoip2.errors.GeoIP2Error as err:
            print(f"Unexpected {err=} while resolving country code for {ip=}")
            pass
    return None