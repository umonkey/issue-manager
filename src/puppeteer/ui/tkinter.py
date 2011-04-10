# vim: set fileencoding=utf-8:

import os
import Tkinter as tk

import puppeteer.github
import puppeteer.util

class HScrollList(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)

        self.list = tk.Listbox(self, highlightthickness=0)
        self.list.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        self.list.bind('<ButtonRelease-1>', self.on_click)

        self.scrollbar = tk.Scrollbar(self, command=self.list.yview)
        self.list['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    def on_click(self, event):
        pass


class IssueList(HScrollList):
    def __init__(self, master, data, on_selected=None, **kwargs):
        HScrollList.__init__(self, master, **kwargs)

        self.on_selected = on_selected
        self.data = data
        self.issues = []

        for project, issues in data.items():
            self.list.insert(tk.END, project)
            self.issues.append(None)
            for num, issue in issues.items():
                self.list.insert(tk.END, u'    %u: %s' % (int(num), issue['subject']))
                self.issues.append(issue)

    def on_click(self, event):
        lb = event.widget
        idx = int(lb.curselection()[0])
        self.on_selected(self.issues[idx])


class Window():
    def __init__(self):
        self.tk = tk.Tk()
        self.issues = {}

        self.tk.title('GitHub Client')

        self.list = IssueList(self.tk, self.get_data(), on_selected=self.on_selected, width='200px', bd=2)
        self.list.pack(fill=tk.Y, side=tk.LEFT, anchor=tk.W, ipady=4)
        self.list.pack_propagate(0)

        self.body = tk.Text(self.tk, bd=2, highlightthickness=0, wrap=tk.WORD)
        self.body.pack(expand=tk.YES, fill=tk.BOTH, side=tk.RIGHT)

    def on_selected(self, issue):
        # http://effbot.org/tkinterbook/text.htm
        self.body.delete(1.0, tk.END)
        if issue:
            self.body.insert(tk.END, issue['description'])

    def show(self):
        tk.mainloop()

    def load_issues(self):
        self.issues = puppeteer.github.get_project_issues('tmradio/tmradio-client-gtk')
        return self.issues

    def get_data(self):
        cache_fn = os.path.expanduser('~/.puppeteer-cache.json')
        if os.path.exists(cache_fn):
            result = puppeteer.util.load_json(cache_fn)
        else:
            result = {}
            for tracker in puppeteer.util.load_yaml(os.path.expanduser('~/.config/tremor.yaml'))['trackers']:
                if tracker['type'].lower() == 'github':
                    result[tracker['name']] = puppeteer.github.get_project_issues(tracker['name'])
            puppeteer.util.save_json(cache_fn, result)
        return result

if __name__ == '__main__':
    Window().show()
