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
        const wikitext = await HookSet.load(pageTitle);
        const hooks = HookSet.findHooks(wikitext);
        return new HookSet(pageTitle, wikitext, hooks);
    }

    static async load(pageTitle) {
        const api = new mw.Api();
        const params = {
            action: 'parse',
            format: 'json',
            page: pageTitle,
            prop: 'wikitext',
            formatversion: 2,
        };
        let wikitext = null;
        await api.get(params)
            .then((result) => {
                wikitext = wikitext = JSON.parse(result).parse.wikitext;
            });
        return wikitext;
    }

    static findHooks(wikitext) {
        return HookSet.findHookLines(wikitext).map((line) => {
            return Hook.build(line);
        });
    }

    static findHookLines(wikitext) {
        const m = wikitext.match(new RegExp('^<!--Hooks-->$(?<block>.*)^<!--HooksEnd-->$', 'sm'));
        return m.groups.block.split('\n')
            .filter((line) => {
                return line.startsWith('* ... ');
            });
    }
}

module.exports = { HookSet };
