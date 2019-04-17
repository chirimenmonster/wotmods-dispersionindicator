package
{
    import net.wg.infrastructure.base.AbstractWindowView;
    import net.wg.infrastructure.base.AbstractView;

	import flash.display.Sprite;
	import flash.display.StageScaleMode;
	import flash.display.StageAlign;
	import flash.events.Event;      
    import flash.utils.getQualifiedClassName;
    
	import LineContainer;
	import PanelContainer;
	
	/**
	 * ...
	 * @author Chirimen
	 */
	public class Main extends AbstractView
	{
        private var className:String = null;
		private var panel:PanelContainer;
        private var _config:Array;
        private var _style:Object;
        	
        public function Main() : void
        {
            className = getQualifiedClassName(this);
			DebugUtils.LOG_DEBUG_FORMAT("%s: %s", className, "constructor");
            super();
        }
        
		private function createPanel() : void
		{
			DebugUtils.LOG_DEBUG_FORMAT("%s: %s", className, "createPanel");
			panel = new PanelContainer(_config, _style);
			panel.alpha = _style.alpha;
			addChild(panel);
		}
		
        override protected function onPopulate() : void
        {
			DebugUtils.LOG_DEBUG_FORMAT("%s: %s", className, "onPopulate");
            createPanel();
            super.onPopulate();
        }

		public function as_setConfig(settings:Object) : void
        {
			DebugUtils.LOG_DEBUG_FORMAT("%s: %s", className, "as_setConfig");
            _config = settings.stats;
            _style = settings.style;
        }

		public function as_setValue(name:String = null, text:String = null) : void
		{
            //DebugUtils.LOG_DEBUG_FORMAT("%s: %s", className, "as_setValue");
			var child:LineContainer = panel.getChildByName(name) as LineContainer;
			child.valueField.text = text;
		}

		public function as_setPosition(x:int = 0, y:int = 0) : void
		{
            //DebugUtils.LOG_DEBUG_FORMAT("%s: %s", className, "as_setPosition");
			panel.x = x;
			panel.y = y;
		}
	
        public function as_getPanelSize() : Object
        {
			//DebugUtils.LOG_DEBUG_FORMAT("%s: %s", className, "as_getPanelSize");
            return { width: panel.fieldWidth, height: panel.fieldHeight };   
        }
	}
	
}
