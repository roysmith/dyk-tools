"use strict";

// nomination.js
// Distributed under the MIT license
// Source at https://github.com/roysmith/dyk-tools/

class Nomination {
    constructor(title, html) {
        this.title = title;
        this.document = document.implementation.createHTMLDocument()
        this.document.documentElement.innerHTML = html;
    }

    static async build(nominationPageTitle) {
        const html = await $.get('/wiki/' + nominationPageTitle);
        return new Nomination(nominationPageTitle, html);
    }

    /**
    * Find the HookSet this Nomination is part of.
    * 
    * @returns [hookSetTitle, key],
    *     i.e. ["Template:Did you know/Queue/6", "Queue 6"]
    * @returns null if no hookSet can be found
    */
    async findHookSet() {
        const params = {
            action: 'query',
            format: 'json',
            prop: 'linkshere',
            titles: this.title,
            formatversion: 2,
            lhnamespace: 10,  // Template namespace, TODO: don't hardwire number
            lhlimit: 100,
        };
        const api = new mw.Api();
        const result = await api.get(params);
        console.assert(result.batchcomplete, "Incomplete batch");
        console.assert(result.query.pages.length == 1, "pages.length != 1");

        const queuePattern = new RegExp('^Template:Did you know/(?<name>Queue)/(?<number>\\d+)$');
        const prepPattern = new RegExp('^Template:Did you know/(?<name>Prep)aration area (?<number>\\d+)$');
        for (const linkData of result.query.pages[0].linkshere) {
            const hookSetTitle = linkData.title;
            const m = hookSetTitle.match(queuePattern) || hookSetTitle.match(prepPattern);
            if (m) {
                const key = `${m.groups.name} ${m.groups.number}`;
                return [hookSetTitle, key];
            };
        }
        console.log(this.title, "not found in result");
        return null;
    }
}

module.exports = { Nomination };
