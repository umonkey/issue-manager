# vim: set fileencoding=utf-8:

import os
import Tkinter as tk

import puppeteer.github
import puppeteer.util

class HScrollList(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        self.list = tk.Listbox(self)
        self.list.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

        self.scrollbar = tk.Scrollbar(self, command=self.list.yview)
        self.list['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)

class IssueView(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

class Window():
    def __init__(self):
        self.tk = tk.Tk()
        self.issues = {}

        self.tk.title('GitHub Client')

        self.list = HScrollList(self.tk, width='200px', bd=2)
        self.list.pack(fill=tk.Y, side=tk.LEFT, anchor=tk.W, ipady=4)
        self.list.pack_propagate(0)

        self.body = HScrollList(self.tk, bd=2)
        self.body.pack(expand=tk.YES, fill=tk.BOTH, side=tk.RIGHT)

        for project, issues in self.get_data().items():
            self.list.list.insert(tk.END, project)
            for issue in issues.values():
                self.list.list.insert(tk.END, u'  ' + issue['subject'])

        for word in ('four', 'five', 'seven'):
            self.body.list.insert(tk.END, word)

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
