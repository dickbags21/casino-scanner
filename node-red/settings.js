/**
 * Node-RED Settings for Casino Scanner Automation
 * 
 * This file configures Node-RED to work with the Casino Scanner dashboard.
 * Place this in your Node-RED user directory (usually ~/.node-red/)
 * or configure Node-RED to use this settings file.
 */

module.exports = {
    // Editor theme
    editorTheme: {
        projects: {
            enabled: false
        }
    },

    // Function global context
    functionGlobalContext: {
        // Add any global context variables here
        casinoApiUrl: 'http://localhost:8000'
    },

    // HTTP Node settings
    httpNodeRoot: '/',
    httpAdminRoot: '/admin',
    httpStatic: '/home/d/casino/node-red/static',

    // User directory
    userDir: '/home/d/casino/node-red',

    // Flow file
    flowFile: '/home/d/casino/node-red/flows.json',

    // Credential encryption
    credentialSecret: process.env.NODE_RED_CREDENTIAL_SECRET || 'casino-scanner-secret-change-in-production',

    // Logging
    logging: {
        console: {
            level: "info",
            metrics: false,
            audit: false
        }
    },

    // External modules
    externalModules: {
        autoInstall: false,
        autoInstallModules: false,
        palette: {
            allowInstall: true,
            allowUpdate: true,
            allowUpload: true
        },
        modules: {
            allowInstall: true,
            allowList: []
        }
    },

    // Editor settings
    editorTheme: {
        header: {
            title: "Casino Scanner Automation",
            image: "/absolute/path/to/your/header/image", // optional
            url: "http://localhost:8000" // optional url to make the header text/image a link
        },
        deployButton: {
            type: "simple",
            icon: "icons/node-red/deploy.svg"
        },
        menu: {
            "menu-item-import-library": false,
            "menu-item-export-library": false,
            "menu-item-keyboard-shortcuts": false,
            "menu-item-help": {
                label: "Casino Scanner Docs",
                url: "http://localhost:8000/api/docs"
            }
        }
    },

    // Runtime settings
    runtimeState: {
        enabled: false,
        ui: false
    }
};

