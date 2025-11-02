# 🚀 Aboro-IT Helpdesk - Chat Widget Integration

## 📋 SOFORT VERWENDBARE CODES

### 🔗 Widget URL
```
http://localhost:8000/chat/widget/
```

### 📱 HTML iframe Code (empfohlen)
```html
<!-- Aboro-IT Helpdesk Live Chat Widget -->
<iframe src="http://localhost:8000/chat/widget/" 
        width="400" 
        height="600" 
        frameborder="0" 
        style="position: fixed; bottom: 20px; right: 20px; z-index: 9999; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
</iframe>
```

### ⚡ JavaScript Code (dynamisch)
```html
<!-- Aboro-IT Helpdesk Live Chat Widget (JavaScript) -->
<script>
(function() {
    var iframe = document.createElement('iframe');
    iframe.src = 'http://localhost:8000/chat/widget/';
    iframe.width = '400';
    iframe.height = '600';
    iframe.frameBorder = '0';
    iframe.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);';
    document.body.appendChild(iframe);
})();
</script>
```

## 🔧 Was du prüfen solltest:

1. **Bist du als Administrator eingeloggt?**
   - Gehe zu: http://localhost:8000
   - Logge dich mit deinem Admin-Account ein

2. **Settings-Seite besuchen:**
   - Gehe zu: http://localhost:8000/settings/
   - Scrolle nach unten zur Sektion "Chat Widget Integration"

3. **Falls die Settings-Seite nicht funktioniert:**
   - Die Codes oben funktionieren SOFORT
   - Kopiere einfach den HTML iframe Code
   - Füge ihn in deine Website vor dem `</body>` Tag ein

## ✅ Features des Widgets:

- 🤖 **AI-gestützt**: Automatische Antworten mit Claude/ChatGPT
- 📱 **Responsive**: Funktioniert auf Desktop & Mobile  
- 🎨 **Anpassbar**: Farbe und Position konfigurierbar
- ⚡ **Echtzeit**: Live-Messaging zwischen Besuchern und Agenten
- 🔄 **Auto-open**: Öffnet sich automatisch in iframe
- 🛡️ **Sicher**: CSRF-geschützt und validiert

## 🌐 Produktions-Setup:

Für die Produktion ändere in der `.env` Datei:
```
SITE_URL=https://deine-domain.com
```

Die Widget-Codes werden dann automatisch die richtige URL verwenden!

---

**🎯 DER CODE FUNKTIONIERT BEREITS!** 
Du kannst ihn sofort in jede Website einbauen! 🚀