let s:cpo_save=&cpo
set cpo&vim
inoremap <silent> <expr> <Plug>(coc-snippets-expand-jump) coc#_insert_key('notify', 'snippets-expand-jump', 1)
inoremap <silent> <expr> <Plug>(coc-snippets-expand) coc#_insert_key('notify', 'snippets-expand', 1)
inoremap <silent> <Plug>(fzf-maps-i) :call fzf#vim#maps('i', 0)
inoremap <expr> <Plug>(fzf-complete-buffer-line) fzf#vim#complete#buffer_line()
inoremap <expr> <Plug>(fzf-complete-line) fzf#vim#complete#line()
inoremap <expr> <Plug>(fzf-complete-file-ag) fzf#vim#complete#path('ag -l -g ""')
inoremap <expr> <Plug>(fzf-complete-file) fzf#vim#complete#path("find . -path '*/\.*' -prune -o -type f -print -o -type l -print | sed 's:^..::'")
inoremap <expr> <Plug>(fzf-complete-path) fzf#vim#complete#path("find . -path '*/\.*' -prune -o -print | sed '1d;s:^..::'")
inoremap <expr> <Plug>(fzf-complete-word) fzf#vim#complete#word()
inoremap <silent> <Plug>CocRefresh =coc#_complete()
inoremap <silent> <SNR>25_AutoPairsReturn =AutoPairsReturn()
omap <silent> % <Plug>(MatchitOperationForward)
xmap <silent> % <Plug>(MatchitVisualForward)
nmap <silent> % <Plug>(MatchitNormalForward)
omap <silent> [% <Plug>(MatchitOperationMultiBackward)
xmap <silent> [% <Plug>(MatchitVisualMultiBackward)
nmap <silent> [% <Plug>(MatchitNormalMultiBackward)
nnoremap <silent> \bd :Bclose
map \f :Ranger
nnoremap <silent> \pw :call WindowSwap#DeprecatedDo()
nnoremap <silent> \yw :call WindowSwap#DeprecatedMark()
nnoremap <silent> \ww :call WindowSwap#EasyWindowSwap()
vnoremap \P "+P
vnoremap \p "+p
nnoremap \P "+P
nnoremap \p "+p
nnoremap \yy "+yy
nnoremap \y "+y
nnoremap \Y "+yg_
vnoremap \y "+y
nmap \gm <Plug>(git-messenger)
omap <silent> ]% <Plug>(MatchitOperationMultiForward)
xmap <silent> ]% <Plug>(MatchitVisualMultiForward)
nmap <silent> ]% <Plug>(MatchitNormalMultiForward)
xmap a% <Plug>(MatchitVisualTextObject)
vmap gx <Plug>NetrwBrowseXVis
nmap gx <Plug>NetrwBrowseX
omap <silent> g% <Plug>(MatchitOperationBackward)
xmap <silent> g% <Plug>(MatchitVisualBackward)
nmap <silent> g% <Plug>(MatchitNormalBackward)
nmap gcu <Plug>Commentary<Plug>Commentary
nmap gcc <Plug>CommentaryLine
omap gc <Plug>Commentary
nmap gc <Plug>Commentary
xmap gc <Plug>Commentary
vnoremap <silent> <Plug>(coc-snippets-select) :call coc#rpc#notify('doKeymap', ['snippets-select'])
xnoremap <silent> <Plug>(coc-convert-snippet) :call coc#rpc#notify('doKeymap', ['convert-snippet'])
vnoremap <silent> <Plug>(coc-explorer-key-v-ai) :call coc#rpc#request('doKeymap', ['explorer-key-v-ai'])
nnoremap <silent> <Plug>(coc-explorer-key-n-ai) :call coc#rpc#request('doKeymap', ['explorer-key-n-ai'])
vnoremap <silent> <Plug>(coc-explorer-key-v-ii) :call coc#rpc#request('doKeymap', ['explorer-key-v-ii'])
nnoremap <silent> <Plug>(coc-explorer-key-n-ii) :call coc#rpc#request('doKeymap', ['explorer-key-n-ii'])
vnoremap <silent> <Plug>(coc-explorer-key-v-al) :call coc#rpc#request('doKeymap', ['explorer-key-v-al'])
nnoremap <silent> <Plug>(coc-explorer-key-n-al) :call coc#rpc#request('doKeymap', ['explorer-key-n-al'])
vnoremap <silent> <Plug>(coc-explorer-key-v->>) :call coc#rpc#request('doKeymap', ['explorer-key-v->>'])
nnoremap <silent> <Plug>(coc-explorer-key-n->>) :call coc#rpc#request('doKeymap', ['explorer-key-n->>'])
vnoremap <silent> <Plug>(coc-explorer-key-v-<<) :call coc#rpc#request('doKeymap', ['explorer-key-v-<<'])
nnoremap <silent> <Plug>(coc-explorer-key-n-<<) :call coc#rpc#request('doKeymap', ['explorer-key-n-<<'])
vnoremap <silent> <Plug>(coc-explorer-key-v-]C) :call coc#rpc#request('doKeymap', ['explorer-key-v-]C'])
nnoremap <silent> <Plug>(coc-explorer-key-n-]C) :call coc#rpc#request('doKeymap', ['explorer-key-n-]C'])
vnoremap <silent> <Plug>(coc-explorer-key-v-[C) :call coc#rpc#request('doKeymap', ['explorer-key-v-[C'])
nnoremap <silent> <Plug>(coc-explorer-key-n-[C) :call coc#rpc#request('doKeymap', ['explorer-key-n-[C'])
vnoremap <silent> <Plug>(coc-explorer-key-v-]c) :call coc#rpc#request('doKeymap', ['explorer-key-v-]c'])
nnoremap <silent> <Plug>(coc-explorer-key-n-]c) :call coc#rpc#request('doKeymap', ['explorer-key-n-]c'])
vnoremap <silent> <Plug>(coc-explorer-key-v-[c) :call coc#rpc#request('doKeymap', ['explorer-key-v-[c'])
nnoremap <silent> <Plug>(coc-explorer-key-n-[c) :call coc#rpc#request('doKeymap', ['explorer-key-n-[c'])
vnoremap <silent> <Plug>(coc-explorer-key-v-]D) :call coc#rpc#request('doKeymap', ['explorer-key-v-]D'])
nnoremap <silent> <Plug>(coc-explorer-key-n-]D) :call coc#rpc#request('doKeymap', ['explorer-key-n-]D'])
vnoremap <silent> <Plug>(coc-explorer-key-v-[D) :call coc#rpc#request('doKeymap', ['explorer-key-v-[D'])
nnoremap <silent> <Plug>(coc-explorer-key-n-[D) :call coc#rpc#request('doKeymap', ['explorer-key-n-[D'])
vnoremap <silent> <Plug>(coc-explorer-key-v-]d) :call coc#rpc#request('doKeymap', ['explorer-key-v-]d'])
nnoremap <silent> <Plug>(coc-explorer-key-n-]d) :call coc#rpc#request('doKeymap', ['explorer-key-n-]d'])
vnoremap <silent> <Plug>(coc-explorer-key-v-[d) :call coc#rpc#request('doKeymap', ['explorer-key-v-[d'])
nnoremap <silent> <Plug>(coc-explorer-key-n-[d) :call coc#rpc#request('doKeymap', ['explorer-key-n-[d'])
vnoremap <silent> <Plug>(coc-explorer-key-v-]m) :call coc#rpc#request('doKeymap', ['explorer-key-v-]m'])
nnoremap <silent> <Plug>(coc-explorer-key-n-]m) :call coc#rpc#request('doKeymap', ['explorer-key-n-]m'])
vnoremap <silent> <Plug>(coc-explorer-key-v-[m) :call coc#rpc#request('doKeymap', ['explorer-key-v-[m'])
nnoremap <silent> <Plug>(coc-explorer-key-n-[m) :call coc#rpc#request('doKeymap', ['explorer-key-n-[m'])
vnoremap <silent> <Plug>(coc-explorer-key-v-]i) :call coc#rpc#request('doKeymap', ['explorer-key-v-]i'])
nnoremap <silent> <Plug>(coc-explorer-key-n-]i) :call coc#rpc#request('doKeymap', ['explorer-key-n-]i'])
vnoremap <silent> <Plug>(coc-explorer-key-v-[i) :call coc#rpc#request('doKeymap', ['explorer-key-v-[i'])
nnoremap <silent> <Plug>(coc-explorer-key-n-[i) :call coc#rpc#request('doKeymap', ['explorer-key-n-[i'])
vnoremap <silent> <Plug>(coc-explorer-key-v-]]) :call coc#rpc#request('doKeymap', ['explorer-key-v-]]'])
nnoremap <silent> <Plug>(coc-explorer-key-n-]]) :call coc#rpc#request('doKeymap', ['explorer-key-n-]]'])
vnoremap <silent> <Plug>(coc-explorer-key-v-[[) :call coc#rpc#request('doKeymap', ['explorer-key-v-[['])
nnoremap <silent> <Plug>(coc-explorer-key-n-[[) :call coc#rpc#request('doKeymap', ['explorer-key-n-[['])
vnoremap <silent> <Plug>(coc-explorer-key-v-gb) :call coc#rpc#request('doKeymap', ['explorer-key-v-gb'])
nnoremap <silent> <Plug>(coc-explorer-key-n-gb) :call coc#rpc#request('doKeymap', ['explorer-key-n-gb'])
vnoremap <silent> <Plug>(coc-explorer-key-v-gf) :call coc#rpc#request('doKeymap', ['explorer-key-v-gf'])
nnoremap <silent> <Plug>(coc-explorer-key-n-gf) :call coc#rpc#request('doKeymap', ['explorer-key-n-gf'])
vnoremap <silent> <Plug>(coc-explorer-key-v-F) :call coc#rpc#request('doKeymap', ['explorer-key-v-F'])
nnoremap <silent> <Plug>(coc-explorer-key-n-F) :call coc#rpc#request('doKeymap', ['explorer-key-n-F'])
vnoremap <silent> <Plug>(coc-explorer-key-v-f) :call coc#rpc#request('doKeymap', ['explorer-key-v-f'])
nnoremap <silent> <Plug>(coc-explorer-key-n-f) :call coc#rpc#request('doKeymap', ['explorer-key-n-f'])
vnoremap <silent> <Plug>(coc-explorer-key-v-gd) :call coc#rpc#request('doKeymap', ['explorer-key-v-gd'])
nnoremap <silent> <Plug>(coc-explorer-key-n-gd) :call coc#rpc#request('doKeymap', ['explorer-key-n-gd'])
vnoremap <silent> <Plug>(coc-explorer-key-v-X) :call coc#rpc#request('doKeymap', ['explorer-key-v-X'])
nnoremap <silent> <Plug>(coc-explorer-key-n-X) :call coc#rpc#request('doKeymap', ['explorer-key-n-X'])
vnoremap <silent> <Plug>(coc-explorer-key-v-[esc]) :call coc#rpc#request('doKeymap', ['explorer-key-v-[esc]'])
nnoremap <silent> <Plug>(coc-explorer-key-n-[esc]) :call coc#rpc#request('doKeymap', ['explorer-key-n-[esc]'])
vnoremap <silent> <Plug>(coc-explorer-key-v-q) :call coc#rpc#request('doKeymap', ['explorer-key-v-q'])
nnoremap <silent> <Plug>(coc-explorer-key-n-q) :call coc#rpc#request('doKeymap', ['explorer-key-n-q'])
vnoremap <silent> <Plug>(coc-explorer-key-v-?) :call coc#rpc#request('doKeymap', ['explorer-key-v-?'])
nnoremap <silent> <Plug>(coc-explorer-key-n-?) :call coc#rpc#request('doKeymap', ['explorer-key-n-?'])
vnoremap <silent> <Plug>(coc-explorer-key-v-R) :call coc#rpc#request('doKeymap', ['explorer-key-v-R'])
nnoremap <silent> <Plug>(coc-explorer-key-n-R) :call coc#rpc#request('doKeymap', ['explorer-key-n-R'])
vnoremap <silent> <Plug>(coc-explorer-key-v-g.) :call coc#rpc#request('doKeymap', ['explorer-key-v-g.'])
nnoremap <silent> <Plug>(coc-explorer-key-n-g.) :call coc#rpc#request('doKeymap', ['explorer-key-n-g.'])
vnoremap <silent> <Plug>(coc-explorer-key-v-zh) :call coc#rpc#request('doKeymap', ['explorer-key-v-zh'])
nnoremap <silent> <Plug>(coc-explorer-key-n-zh) :call coc#rpc#request('doKeymap', ['explorer-key-n-zh'])
vnoremap <silent> <Plug>(coc-explorer-key-v-r) :call coc#rpc#request('doKeymap', ['explorer-key-v-r'])
nnoremap <silent> <Plug>(coc-explorer-key-n-r) :call coc#rpc#request('doKeymap', ['explorer-key-n-r'])
vnoremap <silent> <Plug>(coc-explorer-key-v-A) :call coc#rpc#request('doKeymap', ['explorer-key-v-A'])
nnoremap <silent> <Plug>(coc-explorer-key-n-A) :call coc#rpc#request('doKeymap', ['explorer-key-n-A'])
vnoremap <silent> <Plug>(coc-explorer-key-v-a) :call coc#rpc#request('doKeymap', ['explorer-key-v-a'])
nnoremap <silent> <Plug>(coc-explorer-key-n-a) :call coc#rpc#request('doKeymap', ['explorer-key-n-a'])
vnoremap <silent> <Plug>(coc-explorer-key-v-dF) :call coc#rpc#request('doKeymap', ['explorer-key-v-dF'])
nnoremap <silent> <Plug>(coc-explorer-key-n-dF) :call coc#rpc#request('doKeymap', ['explorer-key-n-dF'])
vnoremap <silent> <Plug>(coc-explorer-key-v-df) :call coc#rpc#request('doKeymap', ['explorer-key-v-df'])
nnoremap <silent> <Plug>(coc-explorer-key-n-df) :call coc#rpc#request('doKeymap', ['explorer-key-n-df'])
vnoremap <silent> <Plug>(coc-explorer-key-v-p) :call coc#rpc#request('doKeymap', ['explorer-key-v-p'])
nnoremap <silent> <Plug>(coc-explorer-key-n-p) :call coc#rpc#request('doKeymap', ['explorer-key-n-p'])
vnoremap <silent> <Plug>(coc-explorer-key-v-dD) :call coc#rpc#request('doKeymap', ['explorer-key-v-dD'])
nnoremap <silent> <Plug>(coc-explorer-key-n-dD) :call coc#rpc#request('doKeymap', ['explorer-key-n-dD'])
vnoremap <silent> <Plug>(coc-explorer-key-v-dd) :call coc#rpc#request('doKeymap', ['explorer-key-v-dd'])
nnoremap <silent> <Plug>(coc-explorer-key-n-dd) :call coc#rpc#request('doKeymap', ['explorer-key-n-dd'])
vnoremap <silent> <Plug>(coc-explorer-key-v-yY) :call coc#rpc#request('doKeymap', ['explorer-key-v-yY'])
nnoremap <silent> <Plug>(coc-explorer-key-n-yY) :call coc#rpc#request('doKeymap', ['explorer-key-n-yY'])
vnoremap <silent> <Plug>(coc-explorer-key-v-yy) :call coc#rpc#request('doKeymap', ['explorer-key-v-yy'])
nnoremap <silent> <Plug>(coc-explorer-key-n-yy) :call coc#rpc#request('doKeymap', ['explorer-key-n-yy'])
vnoremap <silent> <Plug>(coc-explorer-key-v-yn) :call coc#rpc#request('doKeymap', ['explorer-key-v-yn'])
nnoremap <silent> <Plug>(coc-explorer-key-n-yn) :call coc#rpc#request('doKeymap', ['explorer-key-n-yn'])
vnoremap <silent> <Plug>(coc-explorer-key-v-yp) :call coc#rpc#request('doKeymap', ['explorer-key-v-yp'])
nnoremap <silent> <Plug>(coc-explorer-key-n-yp) :call coc#rpc#request('doKeymap', ['explorer-key-n-yp'])
vnoremap <silent> <Plug>(coc-explorer-key-v-II) :call coc#rpc#request('doKeymap', ['explorer-key-v-II'])
nnoremap <silent> <Plug>(coc-explorer-key-n-II) :call coc#rpc#request('doKeymap', ['explorer-key-n-II'])
vnoremap <silent> <Plug>(coc-explorer-key-v-Ic) :call coc#rpc#request('doKeymap', ['explorer-key-v-Ic'])
nnoremap <silent> <Plug>(coc-explorer-key-n-Ic) :call coc#rpc#request('doKeymap', ['explorer-key-n-Ic'])
vnoremap <silent> <Plug>(coc-explorer-key-v-Il) :call coc#rpc#request('doKeymap', ['explorer-key-v-Il'])
nnoremap <silent> <Plug>(coc-explorer-key-n-Il) :call coc#rpc#request('doKeymap', ['explorer-key-n-Il'])
vnoremap <silent> <Plug>(coc-explorer-key-v-ic) :call coc#rpc#request('doKeymap', ['explorer-key-v-ic'])
nnoremap <silent> <Plug>(coc-explorer-key-n-ic) :call coc#rpc#request('doKeymap', ['explorer-key-n-ic'])
vnoremap <silent> <Plug>(coc-explorer-key-v-il) :call coc#rpc#request('doKeymap', ['explorer-key-v-il'])
nnoremap <silent> <Plug>(coc-explorer-key-n-il) :call coc#rpc#request('doKeymap', ['explorer-key-n-il'])
vnoremap <silent> <Plug>(coc-explorer-key-v-gs) :call coc#rpc#request('doKeymap', ['explorer-key-v-gs'])
nnoremap <silent> <Plug>(coc-explorer-key-n-gs) :call coc#rpc#request('doKeymap', ['explorer-key-n-gs'])
vnoremap <silent> <Plug>(coc-explorer-key-v-[bs]) :call coc#rpc#request('doKeymap', ['explorer-key-v-[bs]'])
nnoremap <silent> <Plug>(coc-explorer-key-n-[bs]) :call coc#rpc#request('doKeymap', ['explorer-key-n-[bs]'])
vnoremap <silent> <Plug>(coc-explorer-key-v-t) :call coc#rpc#request('doKeymap', ['explorer-key-v-t'])
nnoremap <silent> <Plug>(coc-explorer-key-n-t) :call coc#rpc#request('doKeymap', ['explorer-key-n-t'])
vnoremap <silent> <Plug>(coc-explorer-key-v-E) :call coc#rpc#request('doKeymap', ['explorer-key-v-E'])
nnoremap <silent> <Plug>(coc-explorer-key-n-E) :call coc#rpc#request('doKeymap', ['explorer-key-n-E'])
vnoremap <silent> <Plug>(coc-explorer-key-v-s) :call coc#rpc#request('doKeymap', ['explorer-key-v-s'])
nnoremap <silent> <Plug>(coc-explorer-key-n-s) :call coc#rpc#request('doKeymap', ['explorer-key-n-s'])
vnoremap <silent> <Plug>(coc-explorer-key-v-e) :call coc#rpc#request('doKeymap', ['explorer-key-v-e'])
nnoremap <silent> <Plug>(coc-explorer-key-n-e) :call coc#rpc#request('doKeymap', ['explorer-key-n-e'])
vnoremap <silent> <Plug>(coc-explorer-key-v-[cr]) :call coc#rpc#request('doKeymap', ['explorer-key-v-[cr]'])
nnoremap <silent> <Plug>(coc-explorer-key-n-[cr]) :call coc#rpc#request('doKeymap', ['explorer-key-n-[cr]'])
nnoremap <silent> <Plug>(coc-explorer-key-n-o) :call coc#rpc#request('doKeymap', ['explorer-key-n-o'])
vnoremap <silent> <Plug>(coc-explorer-key-v-[2-LeftMouse]) :call coc#rpc#request('doKeymap', ['explorer-key-v-[2-LeftMouse]'])
nnoremap <silent> <Plug>(coc-explorer-key-n-[2-LeftMouse]) :call coc#rpc#request('doKeymap', ['explorer-key-n-[2-LeftMouse]'])
vnoremap <silent> <Plug>(coc-explorer-key-v-gh) :call coc#rpc#request('doKeymap', ['explorer-key-v-gh'])
nnoremap <silent> <Plug>(coc-explorer-key-n-gh) :call coc#rpc#request('doKeymap', ['explorer-key-n-gh'])
vnoremap <silent> <Plug>(coc-explorer-key-v-gl) :call coc#rpc#request('doKeymap', ['explorer-key-v-gl'])
nnoremap <silent> <Plug>(coc-explorer-key-n-gl) :call coc#rpc#request('doKeymap', ['explorer-key-n-gl'])
vnoremap <silent> <Plug>(coc-explorer-key-v-K) :call coc#rpc#request('doKeymap', ['explorer-key-v-K'])
nnoremap <silent> <Plug>(coc-explorer-key-n-K) :call coc#rpc#request('doKeymap', ['explorer-key-n-K'])
vnoremap <silent> <Plug>(coc-explorer-key-v-J) :call coc#rpc#request('doKeymap', ['explorer-key-v-J'])
nnoremap <silent> <Plug>(coc-explorer-key-n-J) :call coc#rpc#request('doKeymap', ['explorer-key-n-J'])
vnoremap <silent> <Plug>(coc-explorer-key-v-l) :call coc#rpc#request('doKeymap', ['explorer-key-v-l'])
nnoremap <silent> <Plug>(coc-explorer-key-n-l) :call coc#rpc#request('doKeymap', ['explorer-key-n-l'])
vnoremap <silent> <Plug>(coc-explorer-key-v-h) :call coc#rpc#request('doKeymap', ['explorer-key-v-h'])
nnoremap <silent> <Plug>(coc-explorer-key-n-h) :call coc#rpc#request('doKeymap', ['explorer-key-n-h'])
vnoremap <silent> <Plug>(coc-explorer-key-v-[tab]) :call coc#rpc#request('doKeymap', ['explorer-key-v-[tab]'])
nnoremap <silent> <Plug>(coc-explorer-key-n-[tab]) :call coc#rpc#request('doKeymap', ['explorer-key-n-[tab]'])
vnoremap <silent> <Plug>(coc-explorer-key-v-*) :call coc#rpc#request('doKeymap', ['explorer-key-v-*'])
nnoremap <silent> <Plug>(coc-explorer-key-n-*) :call coc#rpc#request('doKeymap', ['explorer-key-n-*'])
nnoremap <silent> <Plug>(coc-bookmark-prev) :call coc#rpc#notify('doKeymap', ['bookmark-prev'])
nnoremap <silent> <Plug>(coc-bookmark-next) :call coc#rpc#notify('doKeymap', ['bookmark-next'])
nnoremap <silent> <Plug>(coc-bookmark-annotate) :call coc#rpc#notify('doKeymap', ['bookmark-annotate'])
nnoremap <silent> <Plug>(coc-bookmark-toggle) :call coc#rpc#notify('doKeymap', ['bookmark-toggle'])
vnoremap <silent> <Plug>NetrwBrowseXVis :call netrw#BrowseXVis()
nnoremap <silent> <Plug>NetrwBrowseX :call netrw#BrowseX(expand((exists("g:netrw_gx")? g:netrw_gx : '<cfile>')),netrw#CheckIfRemote())
vmap <silent> <Plug>(MatchitVisualTextObject) <Plug>(MatchitVisualMultiBackward)o<Plug>(MatchitVisualMultiForward)
onoremap <silent> <Plug>(MatchitOperationMultiForward) :call matchit#MultiMatch("W",  "o")
onoremap <silent> <Plug>(MatchitOperationMultiBackward) :call matchit#MultiMatch("bW", "o")
vnoremap <silent> <Plug>(MatchitVisualMultiForward) :call matchit#MultiMatch("W",  "n")m'gv``
vnoremap <silent> <Plug>(MatchitVisualMultiBackward) :call matchit#MultiMatch("bW", "n")m'gv``
nnoremap <silent> <Plug>(MatchitNormalMultiForward) :call matchit#MultiMatch("W",  "n")
nnoremap <silent> <Plug>(MatchitNormalMultiBackward) :call matchit#MultiMatch("bW", "n")
onoremap <silent> <Plug>(MatchitOperationBackward) :call matchit#Match_wrapper('',0,'o')
onoremap <silent> <Plug>(MatchitOperationForward) :call matchit#Match_wrapper('',1,'o')
vnoremap <silent> <Plug>(MatchitVisualBackward) :call matchit#Match_wrapper('',0,'v')m'gv``
vnoremap <silent> <Plug>(MatchitVisualForward) :call matchit#Match_wrapper('',1,'v')m'gv``
nnoremap <silent> <Plug>(MatchitNormalBackward) :call matchit#Match_wrapper('',0,'n')
nnoremap <silent> <Plug>(MatchitNormalForward) :call matchit#Match_wrapper('',1,'n')
nnoremap <silent> <Plug>(git-messenger-scroll-up-half) :call gitmessenger#scroll(bufnr('%'), 'C-u')
nnoremap <silent> <Plug>(git-messenger-scroll-down-half) :call gitmessenger#scroll(bufnr('%'), 'C-d')
nnoremap <silent> <Plug>(git-messenger-scroll-up-page) :call gitmessenger#scroll(bufnr('%'), 'C-b')
nnoremap <silent> <Plug>(git-messenger-scroll-down-page) :call gitmessenger#scroll(bufnr('%'), 'C-f')
nnoremap <silent> <Plug>(git-messenger-scroll-up-1) :call gitmessenger#scroll(bufnr('%'), 'C-y')
nnoremap <silent> <Plug>(git-messenger-scroll-down-1) :call gitmessenger#scroll(bufnr('%'), 'C-e')
nnoremap <silent> <Plug>(git-messenger-into-popup) :call gitmessenger#into_popup(bufnr('%'))
nnoremap <silent> <Plug>(git-messenger-close) :call gitmessenger#close_popup(bufnr('%'))
nnoremap <silent> <Plug>(git-messenger) :GitMessenger
onoremap <silent> <Plug>(fzf-maps-o) :call fzf#vim#maps('o', 0)
xnoremap <silent> <Plug>(fzf-maps-x) :call fzf#vim#maps('x', 0)
nnoremap <silent> <Plug>(fzf-maps-n) :call fzf#vim#maps('n', 0)
onoremap <silent> <Plug>(coc-classobj-a) :call coc#rpc#request('selectSymbolRange', [v:false, '', ['Interface', 'Struct', 'Class']])
onoremap <silent> <Plug>(coc-classobj-i) :call coc#rpc#request('selectSymbolRange', [v:true, '', ['Interface', 'Struct', 'Class']])
vnoremap <silent> <Plug>(coc-classobj-a) :call coc#rpc#request('selectSymbolRange', [v:false, visualmode(), ['Interface', 'Struct', 'Class']])
vnoremap <silent> <Plug>(coc-classobj-i) :call coc#rpc#request('selectSymbolRange', [v:true, visualmode(), ['Interface', 'Struct', 'Class']])
onoremap <silent> <Plug>(coc-funcobj-a) :call coc#rpc#request('selectSymbolRange', [v:false, '', ['Method', 'Function']])
onoremap <silent> <Plug>(coc-funcobj-i) :call coc#rpc#request('selectSymbolRange', [v:true, '', ['Method', 'Function']])
vnoremap <silent> <Plug>(coc-funcobj-a) :call coc#rpc#request('selectSymbolRange', [v:false, visualmode(), ['Method', 'Function']])
vnoremap <silent> <Plug>(coc-funcobj-i) :call coc#rpc#request('selectSymbolRange', [v:true, visualmode(), ['Method', 'Function']])
nnoremap <silent> <Plug>(coc-cursors-position) :call coc#rpc#request('cursorsSelect', [bufnr('%'), 'position', 'n'])
nnoremap <silent> <Plug>(coc-cursors-word) :call coc#rpc#request('cursorsSelect', [bufnr('%'), 'word', 'n'])
vnoremap <silent> <Plug>(coc-cursors-range) :call coc#rpc#request('cursorsSelect', [bufnr('%'), 'range', visualmode()])
nnoremap <silent> <Plug>(coc-refactor) :call       CocActionAsync('refactor')
nnoremap <silent> <Plug>(coc-command-repeat) :call       CocAction('repeatCommand')
nnoremap <silent> <Plug>(coc-float-jump) :call       coc#float#jump()
nnoremap <silent> <Plug>(coc-float-hide) :call       coc#float#close_all()
nnoremap <silent> <Plug>(coc-fix-current) :call       CocActionAsync('doQuickfix')
nnoremap <silent> <Plug>(coc-openlink) :call       CocActionAsync('openLink')
nnoremap <silent> <Plug>(coc-references-used) :call       CocActionAsync('jumpUsed')
nnoremap <silent> <Plug>(coc-references) :call       CocActionAsync('jumpReferences')
nnoremap <silent> <Plug>(coc-type-definition) :call       CocActionAsync('jumpTypeDefinition')
nnoremap <silent> <Plug>(coc-implementation) :call       CocActionAsync('jumpImplementation')
nnoremap <silent> <Plug>(coc-declaration) :call       CocActionAsync('jumpDeclaration')
nnoremap <silent> <Plug>(coc-definition) :call       CocActionAsync('jumpDefinition')
nnoremap <silent> <Plug>(coc-diagnostic-prev-error) :call       CocActionAsync('diagnosticPrevious', 'error')
nnoremap <silent> <Plug>(coc-diagnostic-next-error) :call       CocActionAsync('diagnosticNext',     'error')
nnoremap <silent> <Plug>(coc-diagnostic-prev) :call       CocActionAsync('diagnosticPrevious')
nnoremap <silent> <Plug>(coc-diagnostic-next) :call       CocActionAsync('diagnosticNext')
nnoremap <silent> <Plug>(coc-diagnostic-info) :call       CocActionAsync('diagnosticInfo')
nnoremap <silent> <Plug>(coc-format) :call       CocActionAsync('format')
nnoremap <silent> <Plug>(coc-rename) :call       CocActionAsync('rename')
nnoremap <Plug>(coc-codeaction-line) :call       CocActionAsync('codeAction',         'n')
nnoremap <Plug>(coc-codeaction) :call       CocActionAsync('codeAction',         '')
vnoremap <silent> <Plug>(coc-codeaction-selected) :call       CocActionAsync('codeAction',         visualmode())
vnoremap <silent> <Plug>(coc-format-selected) :call       CocActionAsync('formatSelected',     visualmode())
nnoremap <Plug>(coc-codelens-action) :call       CocActionAsync('codeLensAction')
nnoremap <Plug>(coc-range-select) :call       CocActionAsync('rangeSelect',     '', v:true)
vnoremap <silent> <Plug>(coc-range-select-backward) :call       CocActionAsync('rangeSelect',     visualmode(), v:false)
vnoremap <silent> <Plug>(coc-range-select) :call       CocActionAsync('rangeSelect',     visualmode(), v:true)
xnoremap <silent> <Plug>(QuickScopeToggle) :call quick_scope#Toggle()
nnoremap <silent> <Plug>(QuickScopeToggle) :call quick_scope#Toggle()
nmap <silent> <Plug>CommentaryUndo :echoerr "Change your <Plug>CommentaryUndo map to <Plug>Commentary<Plug>Commentary"
nnoremap <silent> <Plug>(startify-open-buffers) :call startify#open_buffers()
inoremap  u
inoremap  u
inoremap <silent> <expr> " coc#_insert_key('request', 'iIg==0')
inoremap <silent> <expr> ' coc#_insert_key('request', 'iJw==0')
inoremap <silent> <expr> ( coc#_insert_key('request', 'iKA==0')
inoremap <silent> <expr> ) coc#_insert_key('request', 'iKQ==0')
inoremap <silent> <expr> < coc#_insert_key('request', 'iPA==0')
inoremap <silent> <expr> > coc#_insert_key('request', 'iPg==0')
inoremap <silent> <expr> [ coc#_insert_key('request', 'iWw==0')
inoremap <silent> <expr> ] coc#_insert_key('request', 'iXQ==0')
inoremap <silent> <expr> ` coc#_insert_key('request', 'iYA==0')
inoremap <silent> <expr> { coc#_insert_key('request', 'iew==0')
inoremap <silent> <expr> } coc#_insert_key('request', 'ifQ==0')
let &cpo=s:cpo_save
unlet s:cpo_save
set helplang=en
set mouse=a
set pyxversion=3
set runtimepath=~/.config/coc/extensions/node_modules/coc-fzf-preview,~/.config/nvim,~/.vim/plugged/rnvimr,~/.vim/plugged/nvim-colorizer.lua,~/.vim/plugged/vimsence,~/.vim/plugged/vim-windowswap,~/.vim/plugged/dracula,~/.vim/plugged/goyo.vim,~/.vim/plugged/vim-startify,~/.vim/plugged/auto-pairs,~/.vim/plugged/vim-commentary,~/.vim/plugged/quick-scope,~/.vim/plugged/pylance.nvim,~/.vim/plugged/coc.nvim,~/.vim/plugged/deoplete.nvim,~/.vim/plugged/vim-highlightedyank,~/.vim/plugged/fzf,~/.vim/plugged/fzf-preview.vim,~/.vim/plugged/fzf.vim,~/.vim/plugged/vim-fugitive,~/.vim/plugged/ranger.vim,~/.vim/plugged/bclose.vim,~/.vim/plugged/vim-rhubarb,~/.vim/plugged/gv.vim,~/.vim/plugged/neoformat,~/.vim/plugged/git-messenger.vim,~/.vim/plugged/undotree,/etc/xdg/xdg-ubuntu/nvim,/usr/etc/xdg/nvim,/etc/xdg/nvim,/usr/share/kubuntu-default-settings/kf5-settings/nvim,~/.local/share/nvim/site,~/.local/share/nvim/site/pack/vim-flake8/start/vim-flake8,/usr/share/ubuntu/nvim/site,/usr/local/share/nvim/site,/usr/share/nvim/site,/var/lib/snapd/desktop/nvim/site,~/.vim/plugged/vim-polyglot,/snap/nvim/314/usr/share/nvim/runtime,/snap/nvim/314/usr/share/nvim/runtime/pack/dist/opt/matchit,~/.vim/plugged/vim-polyglot/after,/var/lib/snapd/desktop/nvim/site/after,/usr/share/nvim/site/after,/usr/local/share/nvim/site/after,/usr/share/ubuntu/nvim/site/after,~/.local/share/nvim/site/after,/usr/share/kubuntu-default-settings/kf5-settings/nvim/after,/etc/xdg/nvim/after,/usr/etc/xdg/nvim/after,/etc/xdg/xdg-ubuntu/nvim/after,~/.vim/plugged/dracula/after,~/.config/nvim/after,~/.config/coc/extensions/node_modules/coc-explorer,~/.config/coc/extensions/node_modules/coc-snippets
set shiftwidth=2
set shortmess=filnxtToOFAI
set tabstop=2
set termguicolors
set updatetime=300
set viewoptions=folds,cursor,curdir
set wildignore=*.pyc
set window=45
" vim: set ft=vim :
