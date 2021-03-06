package com.chirimen.dispersionindicator
{
    import net.wg.infrastructure.base.AbstractView;
    import flash.utils.getQualifiedClassName;

    import com.chirimen.dispersionindicator.LineContainer;
    import com.chirimen.dispersionindicator.PanelContainer;
	
    /**
     * ...
     * @author Chirimen
     */
    public class IndicatorPanel extends AbstractView
    {
        private var className:String = null;
        private var panel:PanelContainer;
        private var _config:Array = null;
        private var _style:Object = null;

        public function IndicatorPanel() : void
        {
            className = getQualifiedClassName(this);
            DebugUtils.LOG_DEBUG("%s: %s", className, "constructor");
            super();
        }

        public function as_setConfig(settings:Object) : void
        {
            DebugUtils.LOG_DEBUG("%s: %s", className, "as_setConfig");
            _config = settings.stats;
            _style = settings.style;
            panel = new PanelContainer(_config, _style);
            panel.visible = false;
            addChild(panel);
        }

        public function as_setValue(name:String = null, text:String = null) : void
        {
            //DebugUtils.LOG_DEBUG("%s: %s", className, "as_setValue");
            var child:LineContainer = panel.getChildByName(name) as LineContainer;
            child.valueField.text = text;
        }

        public function as_setPosition(x:int = 0, y:int = 0) : void
        {
            //DebugUtils.LOG_DEBUG("%s: %s", className, "as_setPosition");
            panel.x = x;
            panel.y = y;
        }
	
        public function as_getPanelSize() : Object
        {
            DebugUtils.LOG_DEBUG("%s: %s", className, "as_getPanelSize");
            return { width: panel.fieldWidth, height: panel.fieldHeight };   
        }

        public function as_setVisible(visible:int = 0) : void
        {
            if (visible == 0) {
                panel.visible = false;
            } else {
                panel.visible = true;
            }
        }
    }

}
