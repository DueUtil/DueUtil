    window.onload = randomMyInfo;

    function randomMyInfo() {
        /**WARNING!!! ULTRA LAZY JAVASCRIPT.
        Some really lasy line copypasting here.
        This is really just a test for the profile viewer.
        **/

        var names = ["MacDue", "VegladeX", "MrAwais", "Sir Foop", "Derek", "Ultra Cheese 9000", "Mega Moose", "DueUtil", "stupid cat", "b1nzy", "Danny"];

        var stats = ["ATK", "ACCY", "STRG", "WagersWon", "QuestsDone"]

        var weapons = ["None", "Gun", "Laser Gun", "Stick", "Frisby", "Ban Hammer"];

        $('.profile').css('background-image', 'url(backgrounds/' + (Math.floor(Math.random() * 54 + 1)) + '.png)');
        $('.avatar').css('background-image', 'url(avatars/' + (Math.floor(Math.random() * 10 + 1)) + '.jpg)');
        $('.banner').css('background-image', 'url(screens/info_banners/' + (Math.floor(Math.random() * 15 + 1)) + '.png)');
        
        var level = Math.floor(Math.random() * 200 + 1);
        var rank = (Math.floor(level/10)+1);
        $('#username').text(names[Math.floor(Math.random() * names.length)]).attr('class','rank-'+(rank > 9 ? 9 : rank));

        //The stats & level here are just random. Nothing like reall DueUtil.
        $('#level').text("LEVEL " +level );

        for (var index = 0; index < stats.length; index++) {
            if (index <= 2) {
                var value = Math.round((Math.random() * 100 + 1) * 100) / 100;
            } else {
                var value = Math.round((Math.random() * 100 + 1))
            }

            $('#' + stats[index]).text(value);

        }

        var done = [];
        var limit = Math.floor(Math.random() * 8 + 1);
        for (var awardNo = 0; awardNo < 8; awardNo++) {
            if (awardNo <= limit) {
                var award = Math.floor(Math.random() * 25 + 1);
                while (done.indexOf(award) != -1) {
                    award = Math.floor(Math.random() * 25 + 1);
                }
                $('#slot-' + awardNo).css('background-image', 'url(awards/' + award + '.png)');
                done.push(award);
            } else {
                $('#slot-' + awardNo).css('background-image', 'none');
            }
        }

        $('#CASH').text("$" + Math.floor(Math.random() * 999999).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,"));

        $('#WPN').text(weapons[Math.floor(Math.random() * weapons.length)]);

    }
   