# Maintainer: Tristan 
pkgname=webscraper
pkgver=0.1.0
pkgrel=1
pkgdesc="A comprehensive web scraper for extracting various types of information"
arch=('any')
url="https://github.com/frostythesnowman52/webscraper"
license=('MIT')
depends=('python' 'python-requests' 'python-beautifulsoup4')
makedepends=('python-setuptools')
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
    cd "$pkgname-$pkgver"
    python setup.py build
}

package() {
    cd "$pkgname-$pkgver"
    python setup.py install --root="$pkgdir" --optimize=1
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
} 