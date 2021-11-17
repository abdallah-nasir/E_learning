(function($) {

	'use strict';

	$(document).ready(function() {

		/*=============================================>>>>>
		= MEDIA QUERIES =
		===============================================>>>>>*/
		function handleWidthChange(mqlVal) {
			var $grid = $('.posts-masonry');
			if (mqlVal.matches) {

				$grid.masonry('destroy');

				$('.nav-main-item').on('click', function() {
					var $subNav = $('.nav-main-sub', this);
					if ($subNav.length) {
						$(this).addClass('active').siblings().removeClass('active');
					}
				});

			} else {

				$grid.masonry({
					itemSelector: '.post',
					gutter: 60
				});
				$grid.imagesLoaded( function() {
					$grid.masonry('layout');
				});

				$('.nav-main-item').off('click');

			}
		}

		if (window.matchMedia) {
			var mql = window.matchMedia('(max-width: 1023px)');
			mql.addListener(handleWidthChange);
			handleWidthChange(mql);
		}

		/*=============================================>>>>>
		= SHOW/HIDE MAIN NAVIGATION =
		===============================================>>>>>*/
		$('.hamburger').on('click', function() {
			$(this).toggleClass('is-active');
			$('body').toggleClass('nav-main-visible');
		});

		/*=============================================>>>>>
		= CLOSE SITE LOADER =
		===============================================>>>>>*/
		$('.btn-site-loader-close').on('click', function() {
			$('body').addClass('loaded');
		});

		/*=============================================>>>>>
		= SWIPER SLIDESHOW =
		===============================================>>>>>*/
		$('.swiper-container').each(function () {
			var	slider = $(this),
				sliderOptions = slider.data('slideshow-options'),
				defaultOptions = {
					prevButton: $('.swiper-button-prev', slider),
					nextButton: $('.swiper-button-next', slider),
					pagination: $('.swiper-pagination', slider),
					paginationClickable: true,
					loop: true,
					autoplay: 10000,
					spaceBetween: 50,
					effect: 'fade',
					autoHeight: true
				};
			var mySwiper = new Swiper(slider, $.extend(defaultOptions, sliderOptions));
		});

		/*=============================================>>>>>
		= GALLERY =
		===============================================>>>>>*/
		$('.gallery').lightGallery({
			download: false,
			prevHtml: '<i class="fa fa-chevron-left"></i>',
			nextHtml: '<i class="fa fa-chevron-right"></i>',
			thumbWidth: 80,
			thumbMargin: 10
		});

		/*=============================================>>>>>
		= FORMS VALIDATION =
		===============================================>>>>>*/
		$('form').each( function() {
			$(this).validate();
		});

		/*=============================================>>>>>
		= CONTACT FORM SUBMIT =
		===============================================>>>>>*/
		$('.form-contact').submit(function(e){
			e.preventDefault();
			var $form = $(this),
				$submit = $form.find('[type="submit"]');
			if( $form.valid() ){
				var dataString = $form.serialize();
				$submit.after('<div class="loader"></div>');
				$.ajax({
					type: $form.attr('method'),
					url: $form.attr('action'),
					data: dataString,
					success: function() {
						$submit.after('<div class="message message-success">Your message was sent successfully!</div>');
					},
					error: function() {
						$submit.after('<div class="message message-error">Your message wasn\'t sent, please try again.</div>');
					},
					complete: function() {
						$form.find('.loader').remove();
						$form.find('.message').fadeIn();
						setTimeout(function() {
							$form.find('.message').fadeOut(function() {
								$(this).remove();
							});
						}, 5000);
					}
				});
			}
		});

		/*=============================================>>>>>
		= TWEETS =
		===============================================>>>>>*/
		var tweetsId = 'tweets',
		tweetsEl = document.getElementById(tweetsId);
		if (tweetsEl) {
			var tweetsConfig = {
				'profile': {screenName: tweetsEl.getAttribute('data-username')},
				'domId': tweetsId,
				'maxTweets': 2,
				'showInteraction': false
			};
			twitterFetcher.fetch(tweetsConfig);
		}

		/*=============================================>>>>>
		= MAP =
		===============================================>>>>>*/
		var mapEl = document.getElementById('map');
		if (mapEl) {

			L.TileLayer.Grayscale = L.TileLayer.extend({
				options: {
					quotaRed: 21,
					quotaGreen: 71,
					quotaBlue: 8,
					quotaDividerTune: 0,
					quotaDivider: function() {
						return this.quotaRed + this.quotaGreen + this.quotaBlue + this.quotaDividerTune;
					}
				},

				initialize: function (url, options) {
					options = options || {};
					options.crossOrigin = true;
					L.TileLayer.prototype.initialize.call(this, url, options);

					this.on('tileload', function(e) {
						this._makeGrayscale(e.tile);
					});
				},

				_createTile: function () {
					var tile = L.TileLayer.prototype._createTile.call(this);
					tile.crossOrigin = 'Anonymous';
					return tile;
				},

				_makeGrayscale: function (img) {
					if (img.getAttribute('data-grayscaled')) {
						return;
					}

					img.crossOrigin = '';
					var canvas = document.createElement('canvas');
					canvas.width = img.width;
					canvas.height = img.height;
					var ctx = canvas.getContext('2d');
					ctx.drawImage(img, 0, 0);

					var imgd = ctx.getImageData(0, 0, canvas.width, canvas.height);
					var pix = imgd.data;
					for (var i = 0, n = pix.length; i < n; i += 4) {
									pix[i] = pix[i + 1] = pix[i + 2] = (this.options.quotaRed * pix[i] + this.options.quotaGreen * pix[i + 1] + this.options.quotaBlue * pix[i + 2]) / this.options.quotaDivider();
					}
					ctx.putImageData(imgd, 0, 0);
					img.setAttribute('data-grayscaled', true);
					img.src = canvas.toDataURL();
				}
			});

			L.tileLayer.grayscale = function (url, options) {
				return new L.TileLayer.Grayscale(url, options);
			};

			var lat = mapEl.getAttribute('data-latitude');
			var lng = mapEl.getAttribute('data-longitude');
			var map = L.map(mapEl, {
				center: [lat, lng],
				zoom: 18,
				'zoomControl': false
			});
			var icon = L.icon({
				iconUrl: 'images/map-marker.png',
				iconSize: [32, 44],
				iconAnchor: [32, 44]
			});

			var zoomControl = L.control.zoom({
				position: 'topright'
			});
			map.addControl(zoomControl);

			L.tileLayer.grayscale('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
			L.marker([lat, lng], {icon: icon}).addTo(map);

		}

	});

	$(window).load(function() {

		$('body').addClass('loaded');

	});

})(jQuery);
