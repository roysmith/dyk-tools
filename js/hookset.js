"use strict";

const { Hook } = require('./hook');

// hookset.js
// Distributed under the MIT license
// Source at https://github.com/roysmith/dyk-tools/

class HookSet {
    constructor(title, wikitext, hooks) {
        this.title = title;
        this.wikitext = wikitext;
        this.hooks = hooks;
    }

    static async build(pageTitle) {
        const wikitext = await HookSet.loadWikitext(pageTitle);
        const hooks = HookSet.findHooks(wikitext);
        return new HookSet(pageTitle, wikitext, hooks);
    }

    static async loadWikitext(pageTitle) {
        const api = new mw.Api();
        const params = {
            action: 'parse',
            format: 'json',
            page: pageTitle,
            prop: 'wikitext',
            formatversion: 2,
        };
        const result = await api.get(params);
        return result.parse.wikitext;
    }

    /**
     * @returns a short name for the hookSet.  This will be a string of the form
     * "Queue 1" or "Prep 5".  It is called a key because it can be used to index
     * into data structures such as that returned by LocalUpdateTimes.
     */
    key() {
        const queuePattern = new RegExp('^Template:Did you know/(?<name>Queue)/(?<number>\\d+)$');
        const prepPattern = new RegExp('^Template:Did you know/(?<name>Prep)aration area (?<number>\\d+)$');
        const m = this.title.match(queuePattern) || this.title.match(prepPattern);
        if (m) {
            return `${m.groups.name} ${m.groups.number}`;
        };
    }

    /**
     * @param string wikitext
     * @returns a generator over Hooks
     */
    static * findHooks(wikitext) {
        for (const line of HookSet.findHookBlock(wikitext)) {
            if (line.startsWith('* ... ')) {
                yield Hook.build(line);
            }
        }
    }

    /**
     * 
     * @param string wikitext 
     * @returns an array of strings (one line per string).  This includes everything
     * between the <!--Hooks--> and <!--HooksEnd--> markers, which should be both a
     * {{main page image/DYK}} template and the actual hooks.
     */
    static findHookBlock(wikitext) {
        const m = wikitext.match(new RegExp('^<!--Hooks-->$(?<block>.*)^<!--HooksEnd-->$', 'sm'));
        return m.groups.block.split('\n');
    }
}

module.exports = { HookSet };
