@wip
Feature: Rundowns

    @auth
    Scenario: Show CRUD
        When we post to "/shows"
        """
        {"name": "Test", "description": "Test description", "duration": 10.5}
        """
        Then we get response code 201

        When we get "/shows"
        Then we get list with 1 items
        """
        {"_items": [{"name": "Test"}]}
        """

        When we get "/shows/#shows._id#"
        Then we get existing resource
        """
        {"name": "Test", "description": "Test description", "duration": 10.5}
        """

        When we patch "/shows/#shows._id#"
        """
        {"name": "Updated", "duration": 11.1}
        """
        Then we get OK response

        When we delete "/shows/#shows._id#"
        Then we get OK response

        When we get "/shows"
        Then we get list with 0 items


    @auth
    Scenario: Templates CRUD
        Given "shows"
        """
        [{"name": "Test"}]
        """

        When we post to "/shows/#shows._id#/rundown_templates"
        """
        {
            "name": "test template",
            "air_time": "06:00",
            "headline_template": {
                "prefix": "Marker",
                "separator": "||",
                "date_format": "dd.MM.yyyy"
            }
        }
        """
        Then we get new resource
        """
        {
            "_links": {
                "self": {
                    "href": "/shows/#shows._id#/rundown_templates/#rundown_templates._id#"
                }
            }
        }
        """

        When we patch "/shows/#shows._id#/rundown_templates/#rundown_templates._id#"
        """
        {"schedule": {"is_active": true, "day_of_week": ["MON", "FRI"]}}
        """
        Then we get OK response

        When we get "/shows/#shows._id#/rundown_templates"
        Then we get list with 1 items
        """
        {"_items": [{"schedule": {"is_active": true}}]}
        """

        When we delete "/shows/#shows._id#/rundown_templates/#rundown_templates._id#"
        Then we get OK response

        When we get "/shows/#shows._id#/rundown_templates"
        Then we get list with 0 items

    @auth
    Scenario: Rundown scope
        When we post to "archive"
        """
        {"headline": "test", "scope": "rundowns", "duration": 60}
        """
        Then we get OK response

        When we get "archive"
        Then we get list with 0 items

        When we get "search"
        Then we get list with 0 items

        When we get "archive?scope=rundowns"
        Then we get list with 1 items
        """
        {"_items": [
            {"duration": 60}
        ]}
        """
    
    @auth
    Scenario: Create rundown using template
        Given "shows"
        """
        [
            {"name": "Test"}
        ]
        """
        And "rundown_templates"
        """
        [
            {
                "name": "Test",
                "show": "#shows._id#",
                "headline_template": {
                    "prefix": "Prefix",
                    "separator": "//",
                    "date_format": "%d.%m.%Y"
                },
                "air_time": "06:00"
            }
        ]
        """

        When we post to "/shows/#shows._id#/rundowns"
        """
        {"template": "#rundown_templates._id#", "date": "2022-06-10"}
        """
        Then we get new resource
        """
        {
            "headline": "Prefix // 10.06.2022",
            "_links": {
                "self": {
                    "href": "archive/#rundowns._id#",
                    "title": "Archive"
                }
            }
        }
        """

        When we get "archive?scope=rundowns"
        Then we get list with 1 items
        """
        {"_items": [
            {"headline": "Prefix // 10.06.2022"}
        ]}
        """
