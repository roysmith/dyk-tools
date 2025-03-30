"use strict";

// localUpdateTimes.js
// Distributed under the MIT license
// Source at https://github.com/roysmith/dyk-tools/

class LocalUpdateTimes {
    constructor(updateTimes) {
        this.updateTimes = updateTimes;
    }

    static async build() {
        const html = await $.get('/wiki/Template:Did_you_know/Queue/LocalUpdateTimes');
        const updateTimes = LocalUpdateTimes.parse(html);
        return new LocalUpdateTimes(updateTimes)
    }

    /**
     * @param {string} html UTF-8 encoded HTML from {{Did you know/Queue/LocalUpdateTimes}}
     * @return an object mapping queue/prep names to times
     */
    static parse(html) {
        const updateTimes = {};
        $(html).find('table.wikitable > tbody > tr').each(function () {
            const $cells = $(this).find('td');
            if ($cells.length < 1) {
                // This will happen on the header row.
                return;
            }
            // This is ugly; it hard-wires that UTC is in column 3.  We really
            // should parse the table headers to see which is the right column.
            const time = $cells[3].innerHTML.replace('<br>', '&nbsp;').trim();
            const tags = $($cells[0]).text();
            const patterns = [
                /(?<tag>Queue \d)/,
                /(?<tag>Prep \d)/,
            ];
            for (const pattern of patterns) {
                const m = tags.match(pattern);
                if (m) {
                    updateTimes[m.groups.tag] = time;
                }
            }
        });
        return updateTimes;
    }
}

module.exports = { LocalUpdateTimes };
