"use strict";

const { describe } = require('node:test');
const { Hook } = require('./hook');
const { Link } = require('./link');

describe('build', () => {
    it('finds bolded links', () => {
        const hook = Hook.build("... that '''[[Foo|bar]]''' is [[Not me]]?");
        expect(hook).toBeInstanceOf(Hook);
        expect(hook.text).toEqual("... that '''[[Foo|bar]]''' is [[Not me]]?");
        expect(hook.links).toEqual(
            [Link.build('[[Foo|bar]]')],
        );
    });
});

describe('Hook constructor', () => {
    it('finds multiple bolded links', () => {
        const hook = Hook.build("... that '''[[Sound Transit]]''' has 170 pieces of '''[[permanent public art]]''' at its stations and facilities?");
        expect(hook).toBeInstanceOf(Hook);
        expect(hook.links).toEqual([
            Link.build('[[Sound Transit]]'),
            Link.build('[[permanent public art]]'),
        ]);
    });
});
