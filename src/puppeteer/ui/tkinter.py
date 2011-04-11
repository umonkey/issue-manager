# vim: set fileencoding=utf-8:

import os
import webbrowser

import tkFont
import Tkinter as tk

import puppeteer.data
import puppeteer.github
import puppeteer.util

class HScrollList(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        self.list = tk.Listbox(self, highlightthickness=0)
        self.list.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.list.bind('<ButtonRelease-1>', self.on_click)
        self.list.bind('<Double-Button-1>', self.on_double_click)

        self.scrollbar = tk.Scrollbar(self, command=self.list.yview)
        self.list['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    def on_click(self, event):
        pass

    def on_double_click(self, event):
        pass


class IssueList(HScrollList):
    def __init__(self, master, data, on_selected=None, **kwargs):
        HScrollList.__init__(self, master, **kwargs)

        self.on_selected = on_selected
        self.data = data
        self.issues = []

        for project, issues in sorted(data.items(), key=lambda a: a[0]):
            self.list.insert(tk.END, project)
            self.issues.append(None)
            for num, issue in sorted(issues.items(), key=lambda i: i[1]['subject']):
                self.list.insert(tk.END, u'    %s (%u)' % (issue['subject'], int(num)))
                self.issues.append(issue)

    def on_click(self, event):
        lb = event.widget
        idx = int(lb.curselection()[0])
        self.on_selected(self.issues[idx])

    def on_double_click(self, event):
        lb = event.widget
        idx = int(lb.curselection()[0])
        webbrowser.open(self.issues[idx]['url'])


class IssueView(tk.Text):
    def __init__(self, master, **kwargs):
        tk.Text.__init__(self, master, **kwargs)

        font_family = 'Sans-Serif'

        font = tkFont.Font(family=font_family, weight='normal', size=10)
        self.config(font=font)

        font = tkFont.Font(family=font_family, weight='bold', size=10)
        self.tag_config('subject', font=font)

        font = tkFont.Font(family=font_family, weight='normal', size=10)
        self.tag_config('comment', font=font, lmargin1=20, lmargin2=20)

        self.tag_config('link', font=font, foreground='blue', underline=True)
        self.tag_bind('link', '<Enter>', lambda e: self.config(cursor='hand2'))
        self.tag_bind('link', '<Leave>', lambda e: self.config(cursor='arrow'))
        self.tag_bind('link', '<Button-1>', self.on_link_clicked)

    def on_link_clicked(self, event):
        w = event.widget
        x, y = event.x, event.y
        for tag in w.tag_names('@%d,%d' % (x, y)):
            if tag.startswith('href:'):
                webbrowser.open(tag[5:])

    def set_issue(self, issue):
        # http://effbot.org/tkinterbook/text.htm
        self.config(state=tk.NORMAL)
        self.delete(1.0, tk.END)

        if issue:
            self.insert(tk.END, u'Subject: ' + issue['subject'] + u'\n\n', ('subject'))
            self.add_comment(issue['description'])

            if 'comments' in issue:
                for comment in issue['comments']:
                    self.insert(tk.END, u'\n\n\nComment from %s:\n' % comment['user'], ('subject'))
                    self.add_comment(comment['body'])

        self.config(state=tk.DISABLED)

    def add_comment(self, text):
        """Adds some text with support for linking.

        Text is added with the "comment" tag, links also have tags "link" and
        "href:..." which are used by the click handler (on_link_clicked)."""
        prefix = u''
        for line in text.split('\n'):
            for word in line.strip().split(' '):
                if '://' in word:
                    tags = ('comment', 'link', u'href:' + word)
                else:
                    tags = 'comment'
                self.insert(tk.END, prefix + word, tags)
                prefix = u' '
            prefix = u'\n'


class Window():
    def __init__(self):
        self.tk = tk.Tk()

        self.tk.title('GitHub Client')

        self.list = IssueList(self.tk, self.get_data(), on_selected=self.on_selected, width='200px', bd=2)
        self.list.pack(fill=tk.Y, side=tk.LEFT, anchor=tk.W, ipady=4)
        self.list.pack_propagate(0)

        self.body = IssueView(self.tk, bd=2, highlightthickness=0, wrap=tk.WORD, state=tk.DISABLED)
        self.body.pack(expand=tk.YES, fill=tk.BOTH, side=tk.RIGHT)

    def on_selected(self, issue):
        self.body.set_issue(issue)

    def show(self):
        tk.mainloop()

    def get_data(self):
        data = puppeteer.data.get_data()
        count = sum([len(x) for x in data])
        self.tk.title('Open Issues (%u)' % count)
        return data

if __name__ == '__main__':
    Window().show()
