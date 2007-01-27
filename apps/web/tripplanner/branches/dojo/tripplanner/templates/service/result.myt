% window = 'parentNode.parentNode.parentNode.parentNode.parentNode.parentNode'
% json = """<input class="json" id="json%s" type="hidden" value='%s' />""" % (c.json_id, c.json)
% result_comp = m.fetch_next()
% content = '%s\n%s' % (m.scomp(result_comp, **ARGS), json)
% toggle_handler = """dojo.html.toggleDisplay(dojo.html.getElementsByClass('content_pane', %s)[0])""" % window
% close_handler = """byCycle.UI.removeResult(this.%s)""" % window
% collapsible = (c.collapsible == '' or c.collapsible)

<& /widgets/window.myt, id=c.result_id,
                        window_classes='result %s' % c.classes,
                        collapsible=collapsible,
                        title=c.title,
                        toggle_handler=toggle_handler,
                        close_handler=close_handler,
                        content=content &>
