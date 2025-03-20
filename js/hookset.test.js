"use strict";

const fs = require('node:fs');
const { describe } = require('node:test');

const { HookSet } = require('./hookset');
const { Hook, Link } = require('./hook');

function getDocument(pathName) {
    return fs.readFileSync(pathName, 'utf8');
}

describe('constructor', () => {
    it('builds a default instance', () => {
        const hs = new HookSet();
        expect(hs).toBeInstanceOf(HookSet);
    });
});

describe('init', () => {
    it('loads wikitext', async () => {
        const json = getDocument('src/js/Template:Did_you_know/Queue/1@1280703597.json');
        mw.Api.prototype.get = jest.fn()
            .mockResolvedValue(json);

        const hs = new HookSet();
        await hs.init("My Queue");

        expect(mw.Api.prototype.get).toHaveBeenCalledTimes(1);
        expect(mw.Api.prototype.get).toHaveBeenCalledWith({
            action: 'parse',
            format: 'json',
            page: "My Queue",
            prop: 'wikitext',
            formatversion: 2,
        });
        expect(hs.wikitext).toMatch(/^{{DYKbotdo.*}}/);
    });

    it('parses the hooks', async () => {
        const json = JSON.stringify({
            "parse": {
                "wikitext": "Blah blah\n"
                    + "<!--Hooks-->\n"
                    + "{{main page image}}\n"
                    + "* ... that politician '''[[Prasenjit Barman]]''' was credited for leading the restoration of the [[Cooch Behar Palace]]?\n"
                    + "* ... that '''[[Sound Transit]]''' has 170 pieces of '''[[permanent public art]]''' at its stations and facilities?\n"
                    + "<!--HooksEnd-->\n"
                    + "{{flatlist|class=dyk-footer noprint|style=margin-top: 0.5em; text-align: right;}}\n"
            }
        });
        mw.Api.prototype.get = jest.fn()
            .mockResolvedValue(json);

        const hs = new HookSet();
        await hs.init("My Queue");

        expect(hs.hooks).toEqual([
            new Hook("* ... that politician '''[[Prasenjit Barman]]''' was credited for leading the restoration of the [[Cooch Behar Palace]]?"),
            new Hook("* ... that '''[[Sound Transit]]''' has 170 pieces of '''[[permanent public art]]''' at its stations and facilities?")
        ]);
        expect(hs.hooks[0].links.length).toEqual(1);
        expect(hs.hooks[1].links.length).toEqual(2);
    });
});

