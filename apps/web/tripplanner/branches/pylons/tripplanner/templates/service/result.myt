% window = 'parentNode.parentNode.parentNode.parentNode.parentNode.parentNode'
% json = """<input class="json" id="json%s" type="hidden" value='%s' />""" % (c.json_id, c.json)
% result_comp = m.fetch_next()
% content = '%s\n%s' % (m.scomp(result_comp, **ARGS), json)
% toggle_handler = """Element.toggle(document.getElementsByClassName('content_pane', %s)[0])""" % window
% close_handler = """byCycle.UI.removeResult(this.%s)""" % window
% toggleable = (c.toggleable == '' or c.toggleable)

<& /widgets/window.myt, id=c.result_id,
                        window_classes='result %s' % c.classes,
                        toggleable=toggleable,
                        title=c.title,
                        toggle_handler=toggle_handler,
                        close_handler=close_handler,
                        content=content &>
