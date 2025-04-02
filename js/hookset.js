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
        const result = await api.get(params);
        return result.parse.wikitext;
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
